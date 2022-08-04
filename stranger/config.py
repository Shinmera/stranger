import discord
import json
import random
import string

class User():
    __slots__ = 'name', 'roles', 'status'
    
    def __init__(self, name, roles=[], status="regular"):
        self.name = name
        self.roles = set(roles)
        self.status = status

    async def join(self, guild):
        member = guild.get_member_named(self.name)
        if member is not None:
            for role_name in self.roles:
                role = discord.utils.get(guild.roles, name=role_name)
                if role is not None:
                    await member.add_roles(role)
        return self

    async def add_roles(self, roles, guild=None):
        new = self.roles.union(roles)
        if new != self.roles:
            self.roles = new
            if guild:
                await self.join(guild)

    def from_config(config):
        return User(config["name"], config.get("roles", []), config.get("status", "regular"))

    def to_config(self):
        return {
            "name": self.name,
            "roles": list(self.roles),
            "status": self.status
        }

class Message():
    __slots__ = 'id', 'channel', 'name', 'role_map'
    
    def __init__(self, channel, id, name, role_map={}):
        self.channel = channel
        self.id = id
        self.name = name
        self.role_map = role_map

    async def react(self, member, emoji, add=True):
        role_name = self.role_map.get(emoji.name)
        if role_name is not None:
            role = discord.utils.get(member.guild.roles, name=role_name)
            if role is not None:
                if add:
                    await member.add_roles(role)
                else:
                    await member.remove_roles(role)
        return self

    async def add_map(self, emoji, role):
        self.role_map[emoji.name] = role
        await emoji.guild.get_channel(self.channel).get_partial_message(self.id).add_reaction(emoji)

    async def remove_map(self, emoji):
        del self.role_map[emoji.name]
        await emoji.guild.get_channel(self.channel).get_partial_message(self.id).clear_reaction(emoji)

    def from_config(config):
        return Message(config["channel"], config["id"], config["name"], config.get("role_map", {}))

    def to_config(self):
        return {
            "channel": self.channel,
            "id": self.id,
            "name": self.name,
            "role_map": self.role_map,
        }

class Server():
    __slots__ = 'id', 'users', 'messages'

    def __init__(self, id, users={}, messages={}):
        self.id = id
        self.users = users
        self.messages = messages

    async def react(self, member, payload, add=True):
        message = self.messages.get((payload.channel_id, payload.message_id))
        if message is not None:
            await message.react(member, payload.emoji, add)
        return self

    async def join(self, member):
        user = self.users.get(str(member))
        if user is not None:
            await user.join(member.guild)
        return self

    def user(self, name):
        if self.users.get(name) is None:
            self.users[name] = User(name)
        return self.users[name]

    def message(self, name, channel=None, id=None):
        if channel is not None:
            message = Message(channel, id, name)
            self.messages[name] = message
            self.messages[(message.channel, message.id)] = message
        return self.messages.get(name)

    def delete_message(self, message):
        del self.messages[message.name]
        del self.messages[(message.channel, message.id)]
        return self

    def from_config(config):
        users = {}
        for user in config.get("users", []):
            user = User.from_config(user)
            users[user.name] = user
        messages = {}
        for message in config.get("messages", []):
            message = Message.from_config(message)
            messages[message.name] = message
            messages[(message.channel, message.id)] = message
        return Server(config["id"], users, messages)

    def to_config(self):
        return {
            "id": self.id,
            "users": [ x.to_config() for x in self.users.values() ],
            "messages": [ x.to_config() for (k, x) in self.messages.items() if type(k) == str ]
        }

def generate_password(length=16):
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=length))

class Configuration():
    __slots__ = 'servers', 'register_password'

    def __init__(self, servers={}, register_password=generate_password()):
        self.servers = servers
        self.register_password = register_password

    def server(self, id):
        if self.servers.get(id) is None:
            self.servers[id] = Server(id)
        return self.servers[id]

    def from_config(config):
        servers = {}
        for server in config.get("servers", []):
            server = Server.from_config(server)
            servers[server.id] = server
        return Configuration(servers, config.get("register_password", generate_password()))
    
    def to_config(self):
        return {
            "register_password": self.register_password,
            "servers": [ x.to_config() for x in self.servers.values() ]
        }

    def load(file):
        with open(file, 'r', encoding='utf-8') as f:
            return Configuration.from_config(json.load(f))

    def save(self, file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.to_config(), f, ensure_ascii=False, indent=4)
        return self
