import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

COG_PATH = os.path.join(os.path.dirname(__file__), 'cogs')
GUILD_ID = os.getenv('GUILD_ID')


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="$", intents=intents)

    async def setup_hook(self):
        for filename in os.listdir(COG_PATH):
            if filename.endswith('.py'):
                await self.load_extension(f'bot.cogs.{filename[:-3]}')

        guild_id_object = discord.Object(id=int(GUILD_ID))

        # clearing old commands
        # self.tree.clear_commands(guild=guild_id_object)
        # await self.tree.sync(guild=guild_id_object)

        self.tree.copy_global_to(guild=guild_id_object)
        await self.tree.sync(guild=guild_id_object)

