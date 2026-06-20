from config import bot, ID
from telebot import types
from database import execute, fetchall, fetchone
from formatting import format_routin_tasks, markup_for_routin_tasks

ROUTINE_MAP = {
    "утро": "morning",
    "вечер": "evening",
    "неделя": "week",
    "75": "75_soft"
}
HEADING_SEND_MAP = {
    "morning": "УТРЕННЯЯ РУТИНА 🌅\n\n",
    "evening": "ВЕЧЕРНЯЯ РУТИНА 🌃\n\n",
    "week": "НЕДЕЛЬНАЯ РУТИНА 📅\n\n",
    "75_soft": "75 SOFT ⛩\n\n"
}


@bot.message_handler(commands=['routin_change'])
def routin(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        types.KeyboardButton('Утро 🌅'),
        types.KeyboardButton('Вечер 🌃'),
        types.KeyboardButton('Неделя 📅'),
        types.KeyboardButton('75 soft ⛩')
    )

    msg = bot.send_message(
        ID,
        "Какую рутину изменить?",
        reply_markup=markup
    )

    bot.register_next_step_handler(msg, send_routin_for_edit)


def send_routin_for_edit(message):
    list_name = ROUTINE_MAP[message.text.split()[0].lower()]

    tasks = fetchall("""
        SELECT text FROM tasks
        WHERE list_name = ?
        ORDER BY id
    """, (list_name,))

    if not tasks:
        msg_text = ""
    else:
        msg_text = "\n".join([t["text"] for t in tasks])

    msg = bot.send_message(
        ID,
        msg_text if msg_text else "Список пуст",
        reply_markup=types.ReplyKeyboardRemove()
    )

    bot.register_next_step_handler(msg, apply_routin_edit, list_name)


def apply_routin_edit(message, list_name):
    raw_text = message.text.strip()

    execute("DELETE FROM tasks WHERE list_name = ?", (list_name,))

    if raw_text:
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

        for line in lines:
            execute("""
                INSERT INTO tasks (list_name, text, task_time, repeat_time, done)
                VALUES (?, ?, ?, ?, 0)
            """, (
                list_name,
                line,
                "00:00",
                "cron"
            ))

    bot.send_message(ID, "Рутина изменена!")


# EVERYDAY ROUTIN
def send_routin(list_name):
    tasks = fetchall(
        "SELECT * FROM tasks WHERE list_name = ?",
        (list_name,)
    )

    info = HEADING_SEND_MAP[list_name]
    info += format_routin_tasks(tasks)

    markup, undone = markup_for_routin_tasks(
        list_name,
        tasks,
        "done"
    )

    return bot.send_message(
        ID,
        info,
        reply_markup=markup
    )


def send_daily_routin(list_name):
    # сбрасываем выполнение
    execute(
        "UPDATE tasks SET done = 0 WHERE list_name = ?",
        (list_name,)
    )

    # отправляем новую рутину
    message = send_routin(list_name)

    # обновляем закреп
    pin_key = f"{list_name}_pin"

    tmp = fetchone(
        "SELECT value FROM bot_state WHERE key = ?",
        (pin_key,)
    )

    old_pin = int(tmp[0]) if tmp else None

    if old_pin:
        try:
            bot.unpin_chat_message(ID, old_pin)
        except Exception:
            pass

    execute("""
        INSERT OR REPLACE INTO bot_state (key, value)
        VALUES (?, ?)
    """, (pin_key, str(message.message_id)))

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
