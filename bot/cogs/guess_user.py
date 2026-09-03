import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone
import random
from views import GuessUserQuizView

class GuessUser(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.number_of_tries = 10

    async def _get_filtered_messages(self, channel: discord.TextChannel, random_date: datetime) -> list[discord.Message]:
        messages = []
        try:
            async for message in channel.history(limit=30, around=random_date):

                print(f"text: {message.content}, mention: {len(message.mentions)}, attachments: {len(message.attachments)}")
                if message.author.bot or message.content.startswith(('!', '/')):
                    continue

                cleaned_content = message.content
                if message.mentions:
                    for user in message.mentions:
                        cleaned_content = cleaned_content.replace(user.mention, "")
                if message.role_mentions:
                    for role in message.role_mentions:
                        cleaned_content = cleaned_content.replace(role.mention, "")
                if message.mention_everyone:
                    cleaned_content = cleaned_content.replace("@everyone", "")
                has_text = bool(cleaned_content.strip())
                has_attachments = bool(message.attachments)

                if not has_text and not has_attachments:
                    continue

                if len(cleaned_content) < 6 and not has_attachments:
                    continue
                messages.append(message)
        except discord.Forbidden:
            print("forbidden")
        return messages


    @app_commands.command(name="guess-user", description="Generate guessing user quiz")
    @app_commands.describe(
        channel="Choose channel which will be scrapped"
    )
    async def generate_game(self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        await interaction.response.defer()

        start_date = channel.created_at
        random_date = start_date + (datetime.now(timezone.utc) - start_date) * random.random()

        tries = 0
        while tries < self.number_of_tries:
            messages = await self._get_filtered_messages(channel, random_date)
            if len(authors := {m.author for m in messages}) >= 3:
                break
            tries += 1
            random_date = start_date + (datetime.now(timezone.utc) - start_date) * random.random()
        else:
            interaction.followup.send("Algorithm didn't find any messages, or a sufficient number of unique users", ephemeral=True)

        if messages:
            target_message = random.choice(messages)
            timeout = 20
            view = GuessUserQuizView(authors, target_message, timeout=timeout)
            await view.start_view(interaction)
            await view.wait()
        else:
            await interaction.followup.send("Algorithm wasn't able to create a quiz. Remember that at least 3 unique people have to write something on given channel", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(GuessUser(bot))
