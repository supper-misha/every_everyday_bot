from config import bot, ID
from telebot import types
from database import execute, fetchall, fetchone
from formatting import format_routin_tasks, markup_for_routin_tasks

ROUTINE_MAP = {
    "утро": "morning",
    "вечер": "evening"
}
HEADING_SEND_MAP = {
    "morning": "УТРЕННЯЯ РУТИНА 🌅\n\n",
    "evening": "ВЕЧЕРНЯЯ РУТИНА 🌃\n\n"
}
HEADING_DEL_MAP = {
    "morning": "УДАЛЕНИЕ УТРО 🌅\n\n",
    "evening": "УДАЛЕНИЕ ВЕЧЕР 🌃\n\n"
}


# CHANGING ROUTIN
def routin_mode(message):
    mode = message.text

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Утро 🌅')
    btn2 = types.KeyboardButton('Вечер 🌃')
    markup.row(btn1, btn2)

    if mode == 'Добавить ➕':
        message1 = bot.send_message(ID, 'В какую рутину добавить', reply_markup=markup)
        bot.register_next_step_handler(message1, reg_routin, 1, "&")
    elif mode == 'Удалить ➖':
        message1 = bot.send_message(ID, 'Из какой рутины удалить', reply_markup=markup)
        bot.register_next_step_handler(message1, send_delete_routin)


def reg_routin(message, step, list_name):
    if step == 1:
        # GETTING TASK NAME
        message1 = bot.send_message(ID, 'Что делаем', reply_markup=types.ReplyKeyboardRemove())
        list_name = ROUTINE_MAP[message.text.split()[0].lower()]
        bot.register_next_step_handler(message1, reg_routin, 2, list_name)
    else:
        # INSERTING TASK INTO DATABASE
        if list_name == "morning":
            par = ("morning", message.text, "06:00", "cron")
        elif list_name == "evening":
            par = ("evening", message.text, "20:00", "cron")

        execute("""
            INSERT INTO tasks (list_name,text,task_time,repeat_time)
            VALUES (?,?,?,?)
        """, par)

        bot.send_message(ID, "Задача добавлена!", reply_markup=types.ReplyKeyboardRemove())


def send_delete_routin(message):
    list_name = ROUTINE_MAP[message.text.split()[0].lower()]

    tasks = fetchall("SELECT * FROM tasks WHERE list_name = ?", (list_name,))

    info = HEADING_DEL_MAP[list_name]
    info += format_routin_tasks(tasks)

    markup, _ = markup_for_routin_tasks(list_name, tasks, "delete")

    bot.send_message(ID, info, reply_markup=markup)


# EVERYDAY ROUTIN
def send_routin(list_name):
    # SETTING DONE TO 0
    execute("UPDATE tasks SET done = 0 WHERE list_name = ?", (list_name,))

    # GETTING THE TASKS
    tasks = fetchall("SELECT * FROM tasks WHERE list_name = ?", (list_name,))

    # SENDING THE TASKS
    info = HEADING_SEND_MAP[list_name]
    info += format_routin_tasks(tasks)
    markup, undone = markup_for_routin_tasks(list_name, tasks, "done")
    message = bot.send_message(ID, info, reply_markup=markup)

    print("got here")
    # UPDATING THE PIN
    PIN_KEY = f"{list_name}_pin"
    tmp = fetchone("SELECT value FROM bot_state WHERE key = ?", (PIN_KEY,))
    old_pin = int(tmp[0]) if tmp else None
    if old_pin:
        bot.unpin_chat_message(ID, old_pin)

    execute("""
        INSERT OR REPLACE INTO bot_state (key, value)
        VALUES (?, ?)
    """, (PIN_KEY, str(message.message_id)))
    bot.pin_chat_message(ID, message.message_id)

# HANDLERS
@bot.callback_query_handler(func=lambda call: call.data.startswith('done'))
def callback(call):
    _, list_name, task_id = call.data.split('&')

    # SETTING DONE
    execute("""
                    UPDATE tasks
                    SET done = 1
                    WHERE id = ?
    """, (task_id,))

    # GETTING THE TASKS
    tasks = fetchall("SELECT * FROM tasks WHERE list_name = ?", (list_name,))

    # SENDING THE TASKS
    info = HEADING_SEND_MAP[list_name]
    info += format_routin_tasks(tasks)
    markup, undone = markup_for_routin_tasks(list_name, tasks, "done")

    tmp = fetchone("""
            SELECT value FROM bot_state WHERE key = ?
    """, (f"{list_name}_pin",))
    pin = int(tmp[0]) if tmp else None
    if not pin:
        return
    bot.edit_message_text(info, ID, pin, reply_markup=markup)
    if undone == 0:
        bot.unpin_chat_message(ID, pin)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete'))
def delete_callback(call):
    _, list_name, task_id = call.data.split('&')

    execute("""
        DELETE FROM tasks
        WHERE id = ?
    """, (task_id,))

    bot.delete_message(call.message.chat.id, call.message.message_id)

    bot.send_message(ID, "Задача удалена!", reply_markup=types.ReplyKeyboardRemove())
