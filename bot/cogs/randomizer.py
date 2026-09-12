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
RANDOMIZER_100_ROLE=os.getenv("RANDOMIZER_100_ROLE")
RANDOMIZER_0_ROLE=os.getenv("RANDOMIZER_0_ROLE")


class Randomizer(commands.Cog):
    def __init__(self, bot: commands.Bot, user_repository: UserRepository):
        self.bot = bot
        self.user_repo = user_repository

    async def give_role(interaction: discord.Interaction, is_100=True):
        role100 = discord.utils.get(interaction.guild.roles, RANDOMIZER_100_ROLE)
        role0 = discord.utils.get(interaction.guild.roles, RANDOMIZER_0_ROLE)

        if not role100:
            role100 = await interaction.guild.create_role(
                name=RANDOMIZER_100_ROLE,
                color=discord.Color.red(),
                mentionable=True,
                permissions=discord.Permissions()
            )
        if not role0:
            role0 = await interaction.guild.create_role(
                name=RANDOMIZER_0_ROLE,
                color=discord.Color.from_str("#4ec1e8"),
                mentionable=True,
                permissions=discord.Permissions()
            )

        await interaction.user.add_roles(role100 if is_100 else role0)
        await interaction.user.remove_roles(role0 if is_100 else role100)


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
        elif number == 100:
            await interaction.followup.send(f":rotating_light:@everyone {interaction.user.mention} {RANDOMIZER_MESSAGE} {number}% {RANDOMIZER_SPECIAL_MESSAGE}:rotating_light:")
            try:
                await interaction.user.timeout(timedelta(seconds=60))
            except Exception:
                logging.exception("Bot doesn't have permission to time-out users, or user cannot be timed out")
            try:
                await self.give_role(interaction)
            except Exception:
                logging.exception("Bot doesn't have permission to give roles")
        else:
            await interaction.followup.send(f"@everyone {interaction.user.mention} {RANDOMIZER_MESSAGE} {number}%")
            try:
                await self.give_role(interaction, is_100=False)
            except Exception:
                logging.exception("Bot doesn't have permission to give roles")


async def setup(bot: commands.Bot):
    user_repo = UserRepository(AsyncSessionLocal)
    await bot.add_cog(Randomizer(bot, user_repo))
