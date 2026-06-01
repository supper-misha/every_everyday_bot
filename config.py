import telebot
import os

TOKEN = os.getenv("MY_BOT_TOKEN")
ID = int(os.getenv("ADMIN_ID"))
bot = telebot.TeleBot(TOKEN)
