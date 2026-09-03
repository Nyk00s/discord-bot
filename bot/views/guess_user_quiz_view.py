import discord


class GuessUserQuizView(discord.ui.View):
    def __init__(self, authors_list: list[discord.User], quiz_message: discord.Message, timeout=20.0):
        super().__init__(timeout=timeout)
        self.authors_list = authors_list
        self.quiz_message = quiz_message
        self.time_left = timeout
        self.message: discord.Message = None
        self.votes: dict[str, int] = {}
        self.given_votes: set = set()

        for author in self.authors_list:
            custom_id = str(author.id)
            button = discord.ui.Button(
                label=author.display_name,
                style=discord.ButtonStyle.secondary,
                custom_id=custom_id
            )
            self.votes[custom_id] = 0
            button.callback = self.handle_button_click
            self.add_item(button)


    async def start_view(self, interaction: discord.Interaction):
        self.message = await interaction.followup.send(
            content=self._get_formatted_content(),
            view=self
        )

    async def handle_button_click(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if interaction.user.id in self.given_votes:
            return
        self.votes[interaction.data["custom_id"]] += 1
        self.given_votes.add(interaction.user.id)

    async def on_timeout(self):

        for item in self.children:
            item.disabled = True
        
        if self.message:
            try:
                await self.message.edit(
                    content=self._get_formatted_content(is_ended=True),
                    view=None
                )
            except discord.NotFound:
                pass

    def _get_formatted_content(self, is_ended: bool = False) -> str:

        text = self.quiz_message.content or ""

        image_urls = []
        if self.quiz_message.attachments:
            for attachment in self.quiz_message.attachments:
                image_urls.append(attachment.url)

        attachment_text = "\n".join(image_urls) if image_urls else ""

        if not is_ended:
            return (
                f"**Who is the author of given message?**\n"
                f"**The quiz duration is: {self.time_left} sec**\n"
                f"(If you choose answer, you cannot change your vote)\n\n"
                f" > {text} \n{attachment_text}\n"
            )
        else:
            return (
                f"**Time is up!**\n"
                f"**Correct User**: **{self.quiz_message.author.display_name}**\n"
                f"**Context**: {self.quiz_message.jump_url}\n"
                f"{self._generate_fig(self.quiz_message.author.id)}"
                f"**Message:**\n\n {text} \n{attachment_text}\n"
            )

    def _generate_fig(self, correct_author_id) -> str:
        final_fig = "**Final result:**\n\n"
        extra_emotes = [":a:", ":b:", ":ab:", ":abc:", ":abcd:"]
        option_list = "**Options**\n"
        result_list = "**Results**\n"
        total_votes = len(self.given_votes)
        for i, author in enumerate(self.authors_list):
            
            if i < 26:
                emote = f":regional_indicator_" + chr(ord('a') + i) + ":"
            else:
                emote = extra_emotes[26 - i]

            option_list += f"{emote} **{author.display_name} {"✓" if author.id == correct_author_id else ""}**\n"
            if total_votes == 0:
                percentage_votes = 0
            else:
                percentage_votes = (self.votes[str(author.id)] / total_votes) * 100
            rounded_percentage_votes = int(percentage_votes / 10) 
            result_list += emote + "▓" * rounded_percentage_votes + "░" * (10 - rounded_percentage_votes) + f"| {percentage_votes:.1f}% ({self.votes[str(author.id)]}) {"✓" if author.id == correct_author_id else ""}\n"
        result_list += f"\n**Total votes: {total_votes}**\n\n"
        final_fig += option_list + "\n" + result_list
        return final_fig
