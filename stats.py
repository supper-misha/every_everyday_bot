from config import bot, ID
from datetime import datetime
from telebot import types
from database import fetchall, fetchone, execute


# PROGRAMMING
@bot.message_handler(commands=['prog'])
def prog(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Добавить ➕')
    btn2 = types.KeyboardButton('Отредактировать ✏️')
    markup.row(btn1, btn2)

    message = bot.send_message(ID, 'Что делаем?', reply_markup=markup)
    bot.register_next_step_handler(message, prog_mode)


def prog_mode(message):
    text = message.text.lower()
    if text.startswith('добавить'):
        reg_prog_task(message, 1, ())
    elif text.startswith('отредактировать'):
        detail_prog_task(message, 1, ())


def detail_prog_task(message, step, data):
    if step == 1:
        message = bot.send_message(ID, 'Введи дату', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, detail_prog_task, step + 1, data)
    elif step == 2:
        date = message.text
        if date.lower() in ['today', 'сегодня']:
            date = datetime.now().strftime("%Y-%m-%d")
        tasks = fetchall("""
            SELECT *
            FROM problems
            WHERE solve_date = ?
        """, (date,))
        info = 'Изменить задачи\n'
        markup = types.InlineKeyboardMarkup()
        buttons = []
        for id, title, url, date, special, comment in tasks:
            if special: info += '❇️'
            info += f'{title}\n'
            info += f'{url}\n\n'
            buttons.append(types.InlineKeyboardButton(title, callback_data=f'special&{id}'))
        markup.row(*buttons)
        bot.send_message(ID, info, reply_markup=markup)


def reg_prog_task(message, step, data):
    if step == 1:
        message = bot.send_message(ID, 'Введи название задачи', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, reg_prog_task, step + 1, ())
    elif step == 2:
        name = message.text
        message = bot.send_message(ID, 'Введи ссылку')
        bot.register_next_step_handler(message, reg_prog_task, step + 1, (name,))
    elif step == 3:
        name = data[0]
        link = message.text
        today = datetime.now().strftime("%Y-%m-%d")
        data += (link, today)
        execute("""
                INSERT INTO problems (title, url, solve_date, special, comment)
                VALUES (?, ?, ?, ?, ?)
            """, (name, link, today, 0, ""))

        bot.send_message(ID, 'готово')


def send_prog_task(start_date="0000-00-00"):
    tasks = fetchall("""
        SELECT *
        FROM problems
        WHERE solve_date >= ?
        ORDER BY solve_date DESC
    """, (start_date,))
    if start_date == "0000-00-00":
        info = f'ЗА ВСЁ ВРЕМЯ РЕШЕНО {len(tasks)} ЗАДАЧ 💻\n'
    elif start_date == datetime.now().strftime("%Y-%m-%d"):
        info = f'СЕГОДНЯ РЕШЕНО {len(tasks)} ЗАДАЧ 💻\n'
    else:
        info = f'C {start_date} РЕШЕНО {len(tasks)} ЗАДАЧ 💻\n'
    for id, title, url, date, special, comment in tasks:
        if special: info += '❇️ '
        info += f'{title}\n'
        info += f'{url}\n'
        if special:
            info += f'{comment}\n'
        info += '\n'
    bot.send_message(ID, info)


def send_daily_prog():
    date = datetime.now().strftime("%Y-%m-%d")
    send_prog_task(date)


def reg_special_comment(message, task_id):
    comment = message.text

    execute("""
        UPDATE problems
        SET special = 1,
            comment = ?
        WHERE id = ?
    """, (comment, task_id))

    bot.send_message(ID, 'готово')


@bot.callback_query_handler(func=lambda call: call.data.startswith('special'))
def special_callback(call):
    task_id = int(call.data.split('&')[1])

    bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )

    message = bot.send_message(ID, 'Введи комментарий')

    bot.register_next_step_handler(message, reg_special_comment, task_id)
