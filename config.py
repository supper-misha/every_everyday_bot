import telebot
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MY_BOT_TOKEN")
ID = int(os.getenv("ADMIN_ID"))
bot = telebot.TeleBot(TOKEN)
