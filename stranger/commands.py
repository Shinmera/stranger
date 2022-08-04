import discord
import csv
from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_access(self, ctx, context=None):
        user = self.server(ctx).user(str(ctx.author))
        if user.status != "admin": return None
        return user

    def server(self, ctx):
        return self.bot.config.server(ctx.guild.id)

    config = property(lambda self: self.bot.config)

    @commands.command(name='register')
    async def register(self, ctx, password):
        user = self.server(ctx).user(str(ctx.author))
        if password != self.config.register_password: return
    
        user.status = "admin"
        self.bot.save()
        await ctx.message.delete()
        await ctx.send("Ok, registration successful.")
    
    @commands.command(name='add-user-role')
    async def add_user_role(self, ctx, user, role):
        if self.check_access(ctx) is None: return
        
        user = self.server(ctx).user(user)
        user.roles.append(role)
        self.bot.save()
        await user.join(ctx.guild)
        await ctx.reply("Ok, {0} has been assigned to the {1} role.".format(user, role))

    @commands.command(name='import-user-roles')
    async def import_user_roles(self, ctx, f):
        if self.check_access(ctx) is None: return

        server = self.server(ctx)
        i = 0
        with open(f, 'r') as f:
            for row in csv.reader(f):
                if i%10 == 0:
                    await ctx.send("Processed {0} rows".format(i))
                await server.user(row[0]).add_roles(row[1:], ctx.guild)
                i++
        self.bot.save()
        await ctx.reply("Ok, user roles imported.")
        
    
    @commands.command(name='make-emoji-message')
    async def make_emoji_message(self, ctx, channel, name, content):
        if self.check_access(ctx) is None: return
        
        channel = discord.utils.get(ctx.guild.channels, name=channel)
        if channel is None:
            await ctx.reply("No channel named {0} found.".format(channel))
        else:
            message = await channel.send(content)
            message = self.server(ctx).message(name, message.channel.id, message.id)
            self.bot.save()
            await ctx.reply("Ok, message created. You can refer to it with its name: {0}".format(message.name))

    @commands.command(name='delete-emoji-message')
    async def delete_emoji_message(self, ctx, message_name):
        if self.check_access(ctx) is None: return
        
        message = self.server(ctx).message(message_name)
        if message is None:
            await ctx.reply("No emoji message named {0} found.".format(message_name))
        else:
            await ctx.guild.get_channel(message.channel).get_partial_message(message.id).delete()
            self.server(ctx).delete_message(message)
            self.bot.save()
            await ctx.repl("Ok, message deleted.")
    
    @commands.command(name='add-reaction-role')
    async def add_reaction_role(self, ctx, message_name, emoji_name, role):
        if self.check_access(ctx) is None: return
        
        message = self.server(ctx).message(message_name)
        emoji = discord.utils.get(ctx.guild.emojis, name=emoji_name)
        if message is None:
            await ctx.reply("No emoji message named {0} found.".format(message_name))
        elif emoji is None:
            await ctx.reply("No emoji with name {0} found.".format(emoji_name))
        else:
            await message.add_map(emoji, role)
            self.bot.save()
            await ctx.reply("Ok, emoji role added!")
    
    @commands.command(name='remove-reaction-role')
    async def remove_reaction_role(self, ctx, message_name, emoji_name):
        if self.check_access(ctx) is None: return
        
        message = self.server(ctx).message(message_name)
        emoji = discord.utils.get(ctx.guild.emojis, name=emoji_name)
        if message is None:
            await ctx.reply("No emoji message named {0} found.".format(message_name))
        elif emoji is None:
            await ctx.reply("No emoji with name {0} found.".format(emoji_name))
        else:
            await message.remove_map(emoji)
            self.bot.save()
            await ctx.reply("Ok, emoji role removed!")
    
    @commands.command(name='save-config')
    async def save_config(self, ctx):
        if self.check_access(ctx) is None: return
    
        self.bot.save()
        await ctx.reply("Ok, config saved.")
