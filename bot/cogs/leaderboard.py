from discord.ext import commands
from bot.repositories import UserRepository
from discord import app_commands
from bot.database import AsyncSessionLocal
import discord
from bot.models import User


class Leaderboard(commands.Cog):

    def __init__(self, bot: commands.Bot, user_repo: UserRepository):
        self.bot = bot
        self.user_repo = user_repo

    @app_commands.command(name='leaderboard', description="Shows leaderboard of TOP 10 users with the highest points score")
    async def show_leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()
        users = await self.user_repo.get_by_points(10)
        embed = discord.Embed(
            title="Leaderboard",
            description=self.format_table(users),
            color=discord.Color.yellow()
        )
        await interaction.followup.send(embed=embed)

    def format_table(self, users: list[User]) -> str:
        leaderboard = ""
        for i, user in enumerate(users):
            leaderboard += f"**{i + 1}.** {user.user_name} - {user.points}\n"
        return leaderboard


async def setup(bot: commands.Bot):
    user_repo = UserRepository(AsyncSessionLocal)
    await bot.add_cog(Leaderboard(bot, user_repo)) 
