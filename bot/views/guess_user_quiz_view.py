import discord

class GuessUserQuizView(discord.ui.View):
    def __init__(self, authors_list: list[discord.User], target_message: discord.Message, timeout=15.0):
        super().__init__(timeout=timeout)
        self.authors_list = authors_list
        self.target_message = target_message

        for author in self.authors_list:
            button = discord.ui.Button(
                label=author.display_name,
                style=discord.ButtonStyle.secondary,
                custom_id=str(author.id)
            )
            button.callback = self.handle_button_click
            self.add_item(button)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    async def handle_button_click(self, interaction: discord.Interaction):
        pass