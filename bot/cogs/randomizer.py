import os
import discord
from discord.ext import commands
from discord import app_commands
import logging
import random
from datetime import timedelta
from bot.repositories import UserRepository
from bot.database import AsyncSessionLocal
from datetime import datetime


RANDOMIZER_COMMAND_NAME=os.getenv("RANDOMIZER_COMMAND_NAME", "randomize")
RANDOMIZER_MESSAGE=os.getenv("RANDOMIZER_MESSAGE", "randomized")
RANDOMIZER_DESCRIPTION=os.getenv("RANDOMIZER_DESCRIPTION", "Randomize number")
RANDOMIZER_SPECIAL_MESSAGE=os.getenv("RANDOMIZER_SPECIAL_MESSAGE", "Goodbye")

class Randomizer(commands.Cog):
    def __init__(self, bot: commands.Bot, user_repository: UserRepository):
        self.bot = bot
        self.user_repo = user_repository

    @app_commands.command(name=RANDOMIZER_COMMAND_NAME, description=RANDOMIZER_DESCRIPTION)
    async def randomize(self, interaction: discord.Interaction):

        user = await self.user_repo.create_user_or_get(interaction.user.id, interaction.user.name)
        today = datetime.now()
        if not user.randomizer_date or user.randomizer_date.date() != today.date():
            user.randomizer_date = today
            await self.user_repo.update(user)
        else:
            await interaction.response.send_message("You can use randomizer only once per day", ephemeral=True)
            return
        
        await interaction.response.defer()
        number = random.randint(0, 100)
        if 0 < number < 100:
            await interaction.followup.send(f"{interaction.user.mention} {RANDOMIZER_MESSAGE} {number}%")
            return
        elif number == 100:
            await interaction.followup.send(f"@everyone {RANDOMIZER_MESSAGE} {number}%")
            try:
                await interaction.user.timeout(timedelta(seconds=60))
            except:
                logging.warning("Bot doesn't have permission to time-out users, or user cannot be timed out")
            return
        else:
            await interaction.followup.send(f":rotating_light:@everyone {RANDOMIZER_MESSAGE} {number}% {RANDOMIZER_SPECIAL_MESSAGE}:rotating_light:")


async def setup(bot: commands.Bot):
    user_repo = UserRepository(AsyncSessionLocal)
    await bot.add_cog(Randomizer(bot, user_repo))
