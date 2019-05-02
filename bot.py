import asyncio
from datetime import datetime

import discord
from discord.ext import commands

from aiohttp import ClientSession
import asyncpg

import uvloop
import os

from core.context import Context
from discord.ext.commands.view import StringView


class SoupBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=None)
        self._session = None
        self._config = {}
        self._db_pool = None
        self.loop = uvloop.new_event_loop()

        self._db_pool = await asyncpg.create_pool(dsn=self.config['db_dsn'], user=self.config['db_user'], command_timeout=60, loop=self.loop)

        self._load_extensions()


    
    @property
    def config(self):
        if config is None:
            with open('config.json') as f:
                self._config.update(json.load(f))
        return self._config

    @property
    def db_pool(self):
        return self._db_pool
    
    @property
    def session(self):
        if self._session is None:
            self._session = ClientSession(self.loop)
        return self._session
    
    @property
    def token(self):
        return self.config.get('token')

    @property
    def blocked_users(self):
        return self.config.get('blocked_users', {})
    
    @property
    def log_channel(self):
        channel_id = self.config.get('log_channel_id')
        if channel_id is not None:
            return self.get_channel(int(channel_id))
        return None

    def _load_extensions(self):
        """Adds commands automatically"""
         self.remove_command('help')
         for file in os.listdir('cogs'):
            if not file.endswith('.py'):
                continue
            cog = f'cogs.{file[:-3]}'
            try:
                self.load_extension(cog)
            except Exception:
                pass

    async def send_cmd_help(self, ctx):
        cmd = ctx.command
        em = discord.Embed(title=f'Usage: {ctx.prefix + cmd.signature}')
        em.color = discord.Color.red()
        em.description = cmd.help
        return em
    
    async def on_command_error(self, ctx, error):
        send_help = (commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments, commands.UserInputError)
        if isinstance(error, commands.CommandNotFound):  # fails silently
            pass
        elif isinstance(error, send_help):
            _help = await send_cmd_help(ctx)
            await ctx.send(embed=_help)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'This command is on cooldown. Please wait {error.retry_after:.2f}s')
    
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('You do not have the permissions to use this command.')

    async def on_messsage(self, message):
        channel = message.channel
        if message.author.bot:
            return
        self.process_commands(message)

    
    @commands.command()
    async def ping(self, ctx):
        '''Pong! Returns your websocket latency'''
        em = discord.Embed()
        em.title ='Pong! Websocket Latency:'
        em.description = f'{self.ws.latency * 1000:.4f} ms'
        await ctx.send(embed=em)
    
    def format_cmd_help(self, ctx, cmd):
        color = discord.Color.red()
        em = discord.Embed(color=color, description=cmd.help)
        if hasattr(cmd, 'invoke_without_command') and cmd.invoke_without_command:
            em.title = f'`Usage: {ctx.prefix}{cmd.signature}`' 
        else:
            em.title = f'`{ctx.prefix}{cmd.signature}`'
        return em
    
    def format_cog_help(self, ctx, cog):
        signatures = []
        color = discord.Color.red()
        em = discord.Embed(color=color, description=f'*{inspect.getdoc(cog)}*')
        em.title = type(cog).__name__.replace('_', ' ')
        cc = []
        for cmd in self.commands:
            if not cmd.hidden:
                if cmd.instance is cog:
                    cc.append(cmd)
                    signatures.append(len(cmd.name) + len(ctx.prefix))
        max_length = max(signatures)
        abc = sorted(cc, key=lambda x: x.name)
        cmds = ''
        for c in abc:
            cmds += f'`{ctx.prefix + c.name:<{max_length}} '
            cmds += f'{c.short_doc:<{max_length}}`\n'
        em.add_field(name='Commands', value=cmds)

    def format_bot_help(self, ctx)
        
    @commands.command()
    async def help(ctx, *, command: str=None):
        '''Shows this message'''
        if command is not None:
            cog = self.get_cog(command.replace(' ','_').title())

    
    def _load_extensions(self, cogs, path='cogs.'):
        for cog in cogs:
            members = inspect.getmembers(cog)
            for name, member in members:
                if name.startswith('on_'):
                    self.add_listener(member, name)
            try:
                self.load_extension(f'{path}{cog}')
            except Exception as e:
                print(f'LoadError: {cog}\n{type(e).__name__}: {e}')

    async def on_ready(self):



    
    


    
    
    