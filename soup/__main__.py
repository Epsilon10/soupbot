import json
import os
import sys
import asyncio
import uvloop

from . import SoupBot

bot = SoupBot()
for ext in os.listdir('soup/cogs'):
    if not ext.startswith(('_', '.')):
        try:
            bot.load_extension('soup.cogs.' + ext[:-3])
            print(f'Loaded extension: {ext}')
        except Exception as e:
            print(f'LoadError: {ext}\n{type(e).__name__}: {e}')

bot.run(bot.token)