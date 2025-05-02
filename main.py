import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

class AB(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
        await self.tree.sync()

bot = AB()

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    # Only trigger when user joins VC for the first time
    if before.channel is None and after.channel is not None:
        linked_channel_id = 1367889862774226954  # Replace with your text channel ID
        linked_channel = bot.get_channel(linked_channel_id)

        if linked_channel:
            await linked_channel.send(
                f"Welcome {member.mention}! Please mark your attendance using `/present`."
            )

bot.run(TOKEN)
