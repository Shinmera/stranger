import discord
from config import Configuration
from discord.ext import commands

class Client(commands.Bot):    
    def __init__(self, config=None):
        super().__init__(intents=discord.Intents.all(), command_prefix='::')
        self.case_insensitive = True
        if config is not None:
            self.config_file = config
            self.config = Configuration.load(config)
        else:
            self.config_file = 'bot-config.json'
            self.config = Configuration()
        
    async def on_ready(self):
        print('We have logged in as {0.user}, processing guilds...'.format(self))
        async for guild in self.fetch_guilds(limit=None):
            print('Processing {0.name}'.format(guild))
            server = self.config.server(guild.id)
            if server is not None:
                async for member in guild.fetch_members(limit=None):
                    server.join(member)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        self.config.server(payload.guild_id).react(payload, True)

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        self.config.server(payload.guild_id).react(payload, False)

    async def on_member_join(self, member):
        self.config.server(payload.guild_id).join(member)

@commands.command(name='register')
async def add_user_role(ctx, password):
    user = ctx.bot.config.user(ctx.author.discriminator)
    if password != ctx.bot.config.register_password: return

    user.status = "admin"
    await ctx.reply("Ok, registration successful.")

@commands.command(name='add-user-role')
async def add_user_role(ctx, user, role):
    user = ctx.bot.config.user(ctx.author.discriminator)
    if user.status != "admin": return
    
    user = ctx.bot.config.server(ctx.guild.id).user(user)
    user.roles.append(role)
    user.join(ctx.guild)
    await ctx.reply("Ok, {0} has been assigned to the {1} role.".format(user, role))

@commands.command(name='make-emoji-message')
async def make_emoji_message(ctx, channel, name, content):
    user = ctx.bot.config.user(ctx.author.discriminator)
    if user.status != "admin": return
    
    channel = discord.utils.get(ctx.guild.channels, name=channel)
    if channel is None:
        await ctx.reply("No channel named {0} found.".format(channel))
    else:
        message = await channel.send(content)
        message = ctx.bot.config.server(ctx.guild.id).message(name, message.channel.id, message.id)
        await ctx.reply("Ok, message created. You can refer to it with its name: {0}".format(message.name))

@commands.command(name='add-reaction-role')
async def add_reaction_role(ctx, message_name, emoji_name, role):
    user = ctx.bot.config.user(ctx.author.discriminator)
    if user.status != "admin": return
    
    message = ctx.bot.config.server(ctx.guild.id).message(message_name)
    emoji = discord.utils.get(ctx.guild.emojis, name=emoji_name)
    if message is None:
        await ctx.reply("No emoji message named {0} found.".format(message_name))
    else if emoji is None:
        await ctx.reply("No emoji with name {0} found.".format(emoji_name))
    else:
        message.add_map(emoji, role)
        await ctx.reply("Ok, emoji role added!")

@commands.command(name='remove-reaction-role')
async def remove_reaction_role(ctx, message_name, emoji_name):
    user = ctx.bot.config.user(ctx.author.discriminator)
    if user.status != "admin": return
    
    message = ctx.bot.config.server(ctx.guild.id).message(message_name)
    emoji = discord.utils.get(ctx.guild.emojis, name=emoji_name)
    if message is None:
        await ctx.reply("No emoji message named {0} found.".format(message_name))
    else if emoji is None:
        await ctx.reply("No emoji with name {0} found.".format(emoji_name))
    else:
        message.remove_map(emoji)
        await ctx.reply("Ok, emoji role added!")

@commands.command(name='save-config')
async def save_config(ctx):
    user = ctx.bot.config.user(ctx.author.discriminator)
    if user.status != "admin": return

    ctx.bot.config.save(ctx.bot.config_file)
    await ctx.reply("Ok, config saved.")
