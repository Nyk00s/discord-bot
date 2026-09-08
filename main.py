from bot.bot import Bot
import logging
from dotenv import load_dotenv
import os

load_dotenv()

bot = Bot()
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"), log_handler=handler, log_level=logging.DEBUG)