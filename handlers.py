from config import bot, ID
from routin import send_routin, send_daily_routin, HEADING_SEND_MAP
from stats import reg_prog_task, send_prog_task, prog_mode, reg_special_comment
from books import add_book_mode, show_books, send_weekly_books_report, send_daily_books_report


# DEBUG
@bot.message_handler(commands=['send'])
def send(message):
    try:
        send_daily_routin(message.text.split()[1].lower())
    except:
        pass


@bot.message_handler(commands=['send3'])
def send3(message):
    send_prog_task()


@bot.message_handler(commands=['send4'])
def send4(message):
    send_weekly_books_report()
    send_daily_books_report()


# MAIN HANDLERS
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бот запущен!")


@bot.message_handler(commands=['addbook'])
def add_book(message):
    add_book_mode(message)


@bot.message_handler(commands=['books'])
def books(message):
    show_books()


@bot.message_handler(commands=['routin'])
def routin(message):
    parts = message.text.split()
    if len(parts) > 1:
        list_name = parts[1].lower()
        if list_name in HEADING_SEND_MAP.keys():
            send_routin(list_name)
        else:
            bot.send_message(ID, 'Неизвестная рутина')
