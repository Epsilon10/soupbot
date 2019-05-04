import discord
from discord.ext import commands
from .core import utils

class General(Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def ping(self, ctx):
        '''Pong! Returns your websocket latency'''
        em = discord.Embed()
        em.title ='Pong! Websocket Latency:'
        em.description = f'{self.bot.ws.latency * 1000:.4f} ms'
        await ctx.send(embed=em)
        
    @commands.command()
    async def help(self, ctx, *, cmd: str=None):
        if cmd is not None:
            cog = self.bot.get_cog(cmd.replace(' ', '_').title())
            _cmd = self.bot.get_command(cmd)
            if cog is not None:
                em = self.bot.format_cog_help(ctx, cog)
            elif _cmd is not None:
                em = self.bot.format_cmd_help(ctx, _cmd)
            else:
                return await ctx.send('No commands found.')
            return await ctx.send(embed=em)
        pages = []
        for cog in self.bot.cogs.values():
            em = self.bot.format_cog_help(ctx, cog)
            pages.append(em)
        em = self.bot.format_bot_help(ctx)
        pages.append(em)
        paginator_session =  PaginatorSession(ctx, footer=f'Type {ctx.prefix}help <command> for more info on a command.', pages=pages)
        await paginator_session.run()
    
    @commands.command(hidden=True)
    @utils.developer()
    async def reload(self, ctx, cog):
        if cog.lower() == 'all':
            for cog in extensions:
                try:
                    self.bot.unload_extension(f"cogs.{cog}")
                except Exception as e:
                    await ctx.send(f"An error occured while reloading {cog}, error details: \n ```{e}```")
            self.bot.load_extensions(extensions)
            return await ctx.send('All cogs updated successfully :white_check_mark:')
        if cog not in extensions:
            return await ctx.send(f'Cog {cog} does not exist.')
        try:
            self.bot.unload_extension(f"cogs.{cog}")
            await asyncio.sleep(1)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f"An error occured while reloading {cog}, error details: \n ```{e}```")
        else:
            await ctx.send(f"Reloaded the {cog} cog successfully :white_check_mark:")
    
    @commands.command(hidden=True)
    @utils.developer()
    async def update(ctx):
        """Pulls from github and updates bot"""
        await ctx.trigger_typing()
        await ctx.send(f"```{subprocess.run('git pull', stdout=subprocess.PIPE).stdout.decode('utf-8')}```")
        for cog in extensions:
            self.bot.unload_extension(f'{path}{cog}')
        for cog in extensions:
            members = inspect.getmembers(cog)
            for name, member in members:
                if name.startswith('on_'):
                    self.bot.add_listener(member, name)
            try:
                self.bot.load_extension(f'{path}{cog}')
            except Exception as e:
                await ctx.send(f'LoadError: {cog}\n{type(e).__name__}: {e}')
        await ctx.send('All cogs reloaded :white_check_mark:')
    

def setup(bot):
    bot.add_cog(General(bot))