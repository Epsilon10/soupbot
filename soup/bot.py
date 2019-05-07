import asyncio
import datetime

import discord
from discord.ext import commands

from aiohttp import ClientSession
import asyncpg

import uvloop
import os

from soup.core.utils import DotDict
from soup.core import utils
from soup.core.paginator import PaginatorSession

import psutil
import inspect
import traceback
import json


class SoupBot(commands.Bot):
    def __init__(self, debug=False):
        super().__init__(command_prefix='-')
        self._session = None
        self._config = None
        self._db_pool = None
        self.debug = debug
        self.process = psutil.Process()
        self.timed_tasks = []
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self._db_pool = None
        
        self.remove_command('help')
    @property
    def config(self):
        if self._config is None:
            with open('soup/data/config.json') as f:
                self._config = DotDict(json.load(f))
        return self._config
    
    @property
    def db_pool(self):
        if self.db_pool is None:
            self.db_pool = asyncpg.create_pool(dsn=self.config.dsn, user=self.config.db_user)
        return self.db_pool

    @property
    def session(self):
        if self._session is None:
            self._session = ClientSession(loop=self.loop)
        return self._session
    
    @property
    def token(self):
        return self.config.token if not self.debug else self.config.dev_token
        
    @property
    def blocked_users(self):
        return self.config.get('blocked_users', {})
    
    @property
    def log_channel(self):
        channel_id = self.config.log_channel_id
        if channel_id is not None:
            return self.get_channel(int(channel_id))
        return None

    async def send_cmd_help(self, ctx):
        cmd = ctx.command
        em = discord.Embed(title=f'Usage: {ctx.prefix + cmd.signature}')
        em.color = discord.Color.red()
        em.description = cmd.help
        return em
    
    ### Event listeners ###
    
    async def on_command_error(self, ctx, error):
        send_help = (commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments, commands.UserInputError)
        if isinstance(error, commands.CommandNotFound):  # fails silently
            pass
        elif isinstance(error, send_help):
            _help = await self.send_cmd_help(ctx)
            await ctx.send(embed=_help)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'This command is on cooldown. Please wait {error.retry_after:.2f}s')
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('You do not have the permissions to use this command.')
        else:
            error_traceback = traceback.format_exc()

    async def on_messsage(self, message):
        channel = message.channel
        if message.author.bot:
            return
        await self.process_commands(message)
    
    async def on_ready(self):
        await self.change_presence(activity=discord.Game(f"with {len(self.guilds)} servers | -help"), afk=True)
        await self.log_start_up()
        print(r"""
                                ___.           __   
        __________  __ ________\_ |__   _____/   |_ _
        /  ___/  _ \|  |  \____ \ | __ \ /  _ \   __\
        \___ (  <_> )  |  /  |_> > \_\ (  <_> )   |  
        /____  >____/|____/|   __/|___  /\____/|__|  
                           |__|                         
            """
        )
        print('\nSoupbot online!')
    
    async def on_guild_join(self, guild):
        pass

    ## Misc utilitiees ##

    async def process_commands(self, message):
        '''Utilises the Context subclass of discord.Context'''
        ctx = await self.get_context(message, cls=discord.Context)
        if ctx.command is None:
            return
        await self.log_command(ctx)
        await self.invoke(ctx)

    async def log_error(self, error_str):
        em = discord.Embed(color=discord.Color.red())
        em.title = f'{ctx.prefix}{ctx.command.name}'
        em.description = f'```{error_str}```'
        em.set_footer(text=f'Invoked at {str(datetime.datetime.utcnow())}')
        await self.log_channel.send(embed=em)
        await self.log_channel.send(f'<@{self.get_user(self.config.owner_id).id}>')

    async def log_command(self, ctx):
        em = discord.Embed(color=discord.Color.green())
        em.title = f'{ctx.prefix}{ctx.command.name}'
        em.description = f'Invoked by {ctx.message.author.id}'
        em.set_footer(text=f'Invoked at {str(datetime.datetime.utcnow())}')
        await self.log_channel.send(embed=em)
    
    async def log_start_up(self):
        em = discord.Embed()
        channels = sum(1 for g in self.guilds for _ in g.channels)
        em.title = 'Soupbot started!'
        em.add_field(name='Latency', value=f'{self.ws.latency*1000:.2f} ms')
        em.add_field(name='Guilds', value=len(self.guilds))
        em.add_field(name='Channels', value=f'{channels} total')
        memory_usage = self.process.memory_full_info().uss / 1024**2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        em.add_field(name='RAM Usage', value=f'{memory_usage:.2f} MiB')
        em.add_field(name='CPU Usage',value=f'{cpu_usage:.2f}% CPU')
        em.add_field(name='Github', value='[Click Here](https://github.com/Epsilon10/soupbot)')
        em.add_field(name='Invite', value=f'[Click Here]({discord.utils.oauth_url(self.user.id)})')
        em.set_footer(text=f'Bot ID: {self.user.id}')
        await self.log_channel.send(embed=em)
    
    def format_cmd_help(self, ctx, cmd):
        color = discord.Color.red()
        em = discord.Embed(color=color, description=cmd.help)
        print(cmd.signature)
        if hasattr(cmd, 'invoke_without_command') and cmd.invoke_without_command:
            em.title = f'`Usage: {ctx.prefix}{cmd.signature}`' 
        else:
            em.title = f'`{ctx.prefix}{cmd.name}{cmd.signature}`'
        return em
    
    def format_cog_help(self, ctx, cog):
        signatures = []
        color = discord.Color.red()
        em = discord.Embed(color=color, description=f'*{inspect.getdoc(cog)}*')
        em.title = type(cog).__name__.replace('_', ' ')
        cc = []
        print('fasffsd')
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

        return em
    
    def format_bot_help(self, ctx):
        signatures = []
        fmt = ''
        commands = []
        for cmd in self.commands:
            print(type(cmd.instance).__name__)
            if not cmd.hidden:
                if type(cmd.instance).__name__.lower() == 'general':
                    print('thotiana')
                    commands.append(cmd)
                    signatures.append(len(cmd.name) + len(ctx.prefix))
        max_length = max(signatures)
        abc = sorted(commands, key=lambda x: x.name)
        for c in abc:
            fmt += f'`{ctx.prefix + c.name:<{max_length}} '
            fmt += f'{c.short_doc:<{max_length}}`\n'
        em = discord.Embed(title='Bot', color=discord.Color.red())
        em.description = '*Bot related commands*'
        em.add_field(name='Commands', value=fmt)

        return em

    
    ## Bot related commands ##



    
    


    
    
    