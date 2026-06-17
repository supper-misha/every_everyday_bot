from config import bot, ID
from routin import send_routin
from telebot import types
from stats import reg_prog_task, send_prog_task, prog_mode, reg_special_comment
from books import add_book_mode, show_books, send_weekly_books_report,send_daily_books_report


# DEBUG
@bot.message_handler(commands=['send'])
def send(message):
    send_routin("morning")


@bot.message_handler(commands=['send2'])
def send(message):
    send_routin("evening")


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


@bot.message_handler(commands=['prog'])
def prog(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Добавить ➕')
    btn2 = types.KeyboardButton('Отредактировать ✏️')
    markup.row(btn1, btn2)

    message = bot.send_message(ID, 'Что делаем?', reply_markup=markup)
    bot.register_next_step_handler(message, prog_mode)


@bot.message_handler(commands=['addbook'])
def add_book(message):
    add_book_mode(message)


@bot.message_handler(commands=['books'])
def books(message):
    show_books()
