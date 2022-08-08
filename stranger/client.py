import discord
from .config import Configuration
from .commands import Commands
from datetime import datetime

class Client(discord.ext.commands.Bot):
    def __init__(self, config=None):
        super().__init__(intents=discord.Intents.all(), command_prefix='::')
        self.case_insensitive = True
        self.add_cog(Commands(self))
        
        if config is not None:
            self.config_file = config
            self.config = Configuration.load(config)
        else:
            self.config_file = 'bot-config.json'
            self.config = Configuration()
            print('Configuration created. Please register your account as admin using the following message in a channel the bot can see:')
            print('::register {0}'.format(self.config.register_password))
        
    async def on_ready(self):
        print('We have logged in as {0.user}, processing guilds...'.format(self))
        async for guild in self.fetch_guilds(limit=None):
            guild = self.get_guild(guild.id)
            server = self.config.server(guild.id)
            if server is not None:
                print('Processing {0.name}'.format(guild))
                async for member in guild.fetch_members(limit=None, after=self.config.last_check):
                    await server.join(member)
        self.config.last_check = datetime.now()
        print('All done.')

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id != self.user.id:
            member = self.get_guild(payload.guild_id).get_member(payload.user_id)
            await self.config.server(payload.guild_id).react(member, payload, True)

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.user_id != self.user.id:
            member = self.get_guild(payload.guild_id).get_member(payload.user_id)
            await self.config.server(payload.guild_id).react(member, payload, False)

    async def on_member_join(self, member):
        self.config.server(member.guild.id).join(member)

    def save(self):
        self.config.save(self.config_file)
