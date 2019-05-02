from discord.ext import commands
import asyncio

class _ContextDBAcquire:
    __slots__ = ('ctx', 'timeout')

    def __init__(self, ctx, timeout):
        self.ctx = ctx
        self.timeout = timeout

    def __await__(self):
        return self.ctx._acquire(self.timeout).__await__()

    async def __aenter__(self):
        await self.ctx._acquire(self.timeout)
        return self.ctx.db

    async def __aexit__(self, *args):
        await self.ctx.release()

class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_pool = self.bot.db_pool
        self._db = None
        self.config = self.bot.config
    
    @property
    def session(self):
        return self.bot.session
    
    @property
    def db(self):
        return self._db if self._db else self.db_pool
    
    @property
    def config(self):
        return self.config
        
    async def _acquire(self, timeout):
        if self._db is None:
            self._db = self.db_pool.acquire(timeout=timeout)
        return self._db
    
    async def acquire(self, timeout=None):
        return _ContextDBAcquire(self, timeout)
    
    async def release(self):
        if self._db is not None:
            await self.bot.db_pool.release(self._db)
            self._db = None