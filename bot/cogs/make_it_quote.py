import discord
from discord.ext import commands
from discord import app_commands
from utils import generate_image_quote
from discord.app_commands import Choice


class MakeItQuote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="quotify", description="Make a quote of given user and text")
    @app_commands.describe(
        text="Text of the quote",
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

        # filter data to render
        author_image_url = None
        if user:
            author = user.name
            author_image_url = user.display_avatar.url
        elif custom_user:
            author = custom_user
        else:
            author = "Anonymous"

        if custom_image:
            if custom_image.content_type and custom_image.content_type.startswith("image/"):
                author_image_url = custom_image.url
            else:
                await interaction.followup.send("File is not an image", ephemeral=True)
                return     

        # render an image
        image_style = None
        if style:
            image_style = style.value
            

        # generated_image = generate_image_quote(text, author, author_image_url, image_style)


        # send back on server 


        embed = discord.Embed(
            color=discord.Color.blue()
        )
        # embed.set_author(name=author, icon_url=author_image_url)
        if author_image_url:
            embed.set_image(url=author_image_url)
        await interaction.followup.send(embed=embed)
        # await interaction.response.send_message(f"Quotifying... {text}, {author}, {author_image_url}, {style}")

async def setup(bot):
    await bot.add_cog(MakeItQuote(bot))
