from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from bot.rogue_bot import bot

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL_2')
TOKEN = os.getenv('TOKEN')

bot.run(TOKEN)