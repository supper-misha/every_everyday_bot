from config import bot, ID
from routin import send_routin, routin_mode
from telebot import types
import sqlite3
from stats import reg_prog_task, send_prog_task, prog_mode, reg_special_comment
import database


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


# MAIN HANDLERS
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бот запущен!")


@bot.message_handler(commands=['routin'])
def routin(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Добавить ➕')
    btn2 = types.KeyboardButton('Удалить ➖')
    markup.row(btn1, btn2)

    message1 = bot.send_message(ID, 'Что делаем?', reply_markup=markup)
    bot.register_next_step_handler(message1, routin_mode)


@bot.message_handler(commands=['prog'])
def prog(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Добавить ➕')
    btn2 = types.KeyboardButton('Отредактировать ✏️')
    markup.row(btn1, btn2)

    message = bot.send_message(ID, 'Что делаем?', reply_markup=markup)
    bot.register_next_step_handler(message, prog_mode)
