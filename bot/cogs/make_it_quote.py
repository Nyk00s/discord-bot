import discord
from discord.ext import commands
from discord import app_commands
from utils import generate_image_quote
from discord.app_commands import Choice


class MakeItQuote(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.quote_ctx_menu = app_commands.ContextMenu(
            name="Quotify!",
            callback=self.quotify_context_menu
        )
        self.bot.tree.add_command(self.quote_ctx_menu)

    async def cog_unload(self):
        self.bot.tree.remove_command(self.quote_ctx_menu.name, type=self.quote_ctx_menu.type)

    @app_commands.command(name="quotify", description="Make a quote of given user and text")
    @app_commands.describe(
        text="Text of the quote (if you want replied message to be quoted, do not fill)",
        user="User that said quote",
        custom_user="If user does not appear on the server you can write it down",
        custom_image="Custom image that will be rendered. If None then it will take user picture profile. If user is not specified, then default image will be rendered",
        style="Choose style of image"
    )
    @app_commands.choices(style=[
        Choice(name="first", value=1),
        Choice(name="second", value=2)
    ])
    async def quotify(self,
        interaction: discord.Interaction,
        text: str,
        user: discord.Member = None,
        custom_user: str = None,
        custom_image: discord.Attachment = None,
        style: Choice[int] = None
    ):
        await interaction.response.defer()

        author_image= None
        if custom_image:
            if custom_image.content_type and custom_image.content_type.startswith("image/"):
                author_image = custom_image
            else:
                await interaction.followup.send("File is not an image", ephemeral=True)
                return 

        if user:
            author = user.name
            if not author_image:
                author_image = user.display_avatar
        elif custom_user:
            author = custom_user
        else:
            author = "Anonymous"    

        generated_image = await generate_image_quote(text, author, author_image, style.value if style else None)
        await interaction.followup.send(file=generated_image)


    async def quotify_context_menu(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.defer()

        text = message.content
        author = message.author.display_name
        author_image = message.author.display_avatar
        generated_image = await generate_image_quote(text, author, author_image, 1)

        await interaction.followup.send(file=generated_image)   


    async def cog_app_command_error(self, interactions: discord.Interaction, error: app_commands.AppCommandError):
        original_error = getattr(error, "original", error)
        msg = f"Error: {original_error}"
        if interactions.response.is_done():
            await interactions.followup.send(msg, ephemeral=True)
        else:
            await interactions.response.send_message(msg, ephemeral=True)


async def setup(bot):
    await bot.add_cog(MakeItQuote(bot))
