import discord
from discord.ext import commands
import json
import asyncpg

def developer():
    def wrapper(ctx):
        with open('./config.json'):
            devs = ctx.config.get('devs', {})
        if ctx.author.id in devs:
            return True
        raise commands.MissingPermissions('You cannot use this command because you are not a developer.')
    return commands.check(wrapper)

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

