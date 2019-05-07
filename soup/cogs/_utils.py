import discord
from discord.ext import commands

def developer():
    def wrapper(ctx):
        with open('./config.json'):
            devs = ctx.config.get('devs', {})
        if ctx.author.id in devs:
            return True
        raise commands.MissingPermissions('You cannot use this command because you are not a developer.')
    return commands.check(wrapper)
