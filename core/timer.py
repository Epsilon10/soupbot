import datetime
import discord
import asyncio

class AsyncTimer:
    def __init__(self, seconds, timestamp=datetime.datetime.utcnow()):
        self.seconds = seconds
        self.timestamp = timestamp
        self.loop = loop

    def remaining_time(self):
        return (datetime.datetime.utcnow() - self.timestamp)

class UserTimer(AsyncTimer):
    def __init__(self, user_id, guild_id, **kwargs):
        self.guild_id = guild_id
        self.user_id = user_id
        self.handle_args = kwargs
        self.handle = handle
    
    async def sleep_handle(self):
        elapsed_seconds = (datetime.datetime.utcnow() - self.timestamp).total_seconds()
        if elapsed_seconds <= self.seconds:     
            await asyncio.sleep(self.seconds - elasped_seconds)
            return await self.handle(**self.handle_args)


