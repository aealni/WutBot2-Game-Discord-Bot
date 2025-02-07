import altereignModule
import discord
import os
import inspect
from altereignModule import *
from keep_alive import keep_alive

from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.typing = False
intents.presences = False
client = commands.Bot(command_prefix="!", intents=intents)


rpgFunctions = {}

print(dir(altereignModule))
for index in dir(altereignModule):
    obj = getattr(altereignModule, index)
    try:
        if inspect.isfunction(obj):
            for trigger in obj.triggers:
                rpgFunctions.update({trigger : obj})
    except:
        pass

print(rpgFunctions)

@client.event
async def on_ready():
    await altereignModule.on_ready(client)

@client.event
async def on_message(msg):
    for key in rpgFunctions.keys():
        if msg.content.lower().startswith("!" + key):
            print(msg.content)
            await rpgFunctions[key](client, await client.get_context(msg))

keep_alive()
client.run(os.getenv('TOKEN HERE'))