import database
import routin
import handlers
import config
import schedule
import stats

from config import bot
from database import init_database

init_database()
bot.infinity_polling()
