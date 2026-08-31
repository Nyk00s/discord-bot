import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import random
from views import GuessUserQuizView

class GuessUser(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.number_of_tries = 10

    async def _get_filtered_messages(self, interaction: discord.Interaction, random_date: datetime) -> list[discord.Message]:
        messages = []
        async for message in interaction.channel.history(limit=30, around=random_date):
            if (message.author.bot or message.content.startswith(('!', '/'))) or \
                (message.mentions and not message.content):
                continue
            messages.append(message)
        return messages


    @app_commands.command(name="guess-user", description="Generate guessing user quiz")
    async def generate_game(self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()

        start_date = interaction.channel.created_at
        random_date = start_date + (datetime.now() - start_date) * random.random()

        tries = 0
        while tries < self.number_of_tries:
            messages = await self._get_filtered_messages(interaction, random_date)
            if len(authors := {m.author for m in messages}) >= 3:
                break
            tries += 1
            random_date = start_date + (datetime.now() - start_date) * random.random()

        target_message = random.choice(messages)

        view = GuessUserQuizView(authors, target_message)

        message = await interaction.followup.send(
            content=f"Who is the author of given message?\n\n {target_message.content}",
            view=view
        )

        await view.wait()

        await message.edit(
            content=(
                f"STOP\n"
                f"Correct answer: {target_message.author.display_name}\n"
                f"Context: {target_message.jump_url}"
            ),
            view=None
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(GuessUser(bot))