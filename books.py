from config import bot, ID
from telebot import types
from database import execute, fetchall, fetchone
from datetime import datetime, timedelta


# ----------------------------
# FORMATTING
# ----------------------------

def format_book_active(b):
    total_read = fetchone("""
        SELECT SUM(pages_read)
        FROM reading_log
        WHERE book_id = ?
    """, (b["id"],))[0] or 0

    return (
        f"*{b['title']}*\n"
        f"{b['author']}\n"
        f"Страниц {b['total_pages']}, сейчас на {total_read}"
    )


def format_book_report(b, pages):
    total_read = fetchone("""
        SELECT SUM(pages_read)
        FROM reading_log
        WHERE book_id = ?
    """, (b["id"],))[0] or 0

    return (
        f"*{b['title']}*\n"
        f"{b['author']}\n"
        f"Сейчас на {total_read}/{b['total_pages']}, прочитал {pages}"
    )


# ----------------------------
# ADD BOOK
# ----------------------------

def add_book_mode(message):
    msg = bot.send_message(
        message.chat.id,
        "Название книги",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(msg, get_book_author)


def get_book_author(message):
    title = message.text.strip()

    msg = bot.send_message(message.chat.id, "Автор")
    bot.register_next_step_handler(msg, get_book_pages, title)


def get_book_pages(message, title):
    author = message.text.strip()

    msg = bot.send_message(message.chat.id, "Сколько страниц:")
    bot.register_next_step_handler(msg, save_book, title, author)


def save_book(message, title, author):
    try:
        total_pages = int(message.text)
        if total_pages <= 0:
            raise ValueError
    except:
        bot.send_message(message.chat.id, "bug")
        return

    today = datetime.now().strftime("%Y-%m-%d")

    execute("""
        INSERT INTO books (title, author, total_pages, start_date, end_date)
        VALUES (?, ?, ?, ?, NULL)
    """, (title, author, total_pages, today))

    bot.send_message(ID, "📚 Книга добавлена!")


# ----------------------------
# READ MODE (INLINE)
# ----------------------------

@bot.message_handler(commands=['read'])
def read_books(message):
    books = fetchall("SELECT * FROM books WHERE end_date IS NULL")

    if not books:
        bot.send_message(message.chat.id, "Нет активных книг")
        return

    markup = types.InlineKeyboardMarkup()

    for b in books:
        markup.add(
            types.InlineKeyboardButton(
                text=b["title"],
                callback_data=f"book_read&{b['id']}"
            )
        )

    bot.send_message(message.chat.id, "Выбери книгу", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("book_read&"))
def book_read_callback(call):
    _, book_id = call.data.split("&")
    book_id = int(book_id)

    bot.answer_callback_query(call.id)

    msg = bot.send_message(
        call.message.chat.id,
        "На какой странице ты сейчас?"
    )

    bot.register_next_step_handler(msg, save_read_pages, book_id)


def save_read_pages(message, book_id):
    try:
        current_page = int(message.text)
        if current_page <= 0:
            raise ValueError
    except:
        bot.send_message(message.chat.id, "bug")
        return

    today = datetime.now().strftime("%Y-%m-%d")

    total_read = fetchone("""
        SELECT SUM(pages_read)
        FROM reading_log
        WHERE book_id = ?
    """, (book_id,))[0] or 0

    diff = current_page - total_read

    if diff <= 0:
        bot.send_message(message.chat.id, "Ты не продвинулся вперёд")
        return

    execute("""
        INSERT INTO reading_log (book_id, pages_read, date)
        VALUES (?, ?, ?)
    """, (book_id, diff, today))

    total_read = fetchone("""
        SELECT SUM(pages_read)
        FROM reading_log
        WHERE book_id = ?
    """, (book_id,))[0] or 0

    book = fetchone("SELECT * FROM books WHERE id = ?", (book_id,))

    if book and book["total_pages"] > 0:
        if total_read >= book["total_pages"]:
            execute("""
                UPDATE books
                SET end_date = ?
                WHERE id = ?
            """, (today, book_id))

    bot.send_message(ID, "Прогресс обновлён")


# ----------------------------
# DELETE BOOK
# ----------------------------
@bot.message_handler(commands=['delbook'])
def delete_book(message):
    books = fetchall("""
        SELECT *
        FROM books
        ORDER BY end_date IS NOT NULL, title
    """)

    if not books:
        bot.send_message(message.chat.id, "Книг нет")
        return

    markup = types.InlineKeyboardMarkup()

    for b in books:
        markup.add(
            types.InlineKeyboardButton(
                text=b["title"],
                callback_data=f"book_delete&{b['id']}"
            )
        )

    bot.send_message(
        message.chat.id,
        "Выбери книгу для удаления",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("book_delete&"))
def delete_book_callback(call):
    _, book_id = call.data.split("&")
    book_id = int(book_id)

    book = fetchone("""
        SELECT *
        FROM books
        WHERE id = ?
    """, (book_id,))

    if not book:
        bot.answer_callback_query(call.id, "Книга не найдена")
        return

    title = book["title"]

    execute("""
        DELETE FROM reading_log
        WHERE book_id = ?
    """, (book_id,))

    execute("""
        DELETE FROM books
        WHERE id = ?
    """, (book_id,))

    bot.edit_message_text(
        f"Книга *{title}* удалена",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

    bot.answer_callback_query(call.id)


# ----------------------------
# WEEKLY REPORT
# ----------------------------

def send_weekly_books_report():
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    stats = fetchall("""
        SELECT book_id, SUM(pages_read) as pages
        FROM reading_log
        WHERE date >= ?
        GROUP BY book_id
    """, (start_date,))

    if not stats:
        bot.send_message(ID, "За неделю ничего не прочитано 📚")
        return

    msg = "ЗА НЕДЕЛЮ ПРОЧИТАНО 📚\n\n"

    for book_id, pages in stats:
        book = fetchone("SELECT * FROM books WHERE id = ?", (book_id,))

        if not book:
            continue

        msg += format_book_report(book, pages)
        msg += "\n\n"

    bot.send_message(ID, msg, parse_mode="Markdown")


# ----------------------------
# DAILY REPORT
# ----------------------------

def send_daily_books_report():
    today = datetime.now().strftime("%Y-%m-%d")

    stats = fetchall("""
        SELECT book_id, SUM(pages_read) as pages
        FROM reading_log
        WHERE date = ?
        GROUP BY book_id
    """, (today,))

    if not stats:
        bot.send_message(ID, "За сегодня не было чтения 📚")
        return

    msg = "СЕГОДНЯ ПРОЧИТАНО 📚\n"

    for book_id, pages in stats:
        book = fetchone("SELECT * FROM books WHERE id = ?", (book_id,))

        if not book:
            continue

        msg += format_book_report(book, pages)
        msg += "\n\n"

    bot.send_message(ID, msg, parse_mode="Markdown")


# ----------------------------
# SHOW BOOKS
# ----------------------------

def show_books():
    active_books = fetchall("""
        SELECT * FROM books
        WHERE end_date IS NULL
    """)

    finished_books = fetchall("""
        SELECT * FROM books
        WHERE end_date IS NOT NULL
    """)

    msg = "СТАТИСТИКА ЧТЕНИЯ 📒\n\n"

    if active_books:
        msg += "ЧИТАЮ СЕЙЧАС 📖\n"

        for b in active_books:
            msg += format_book_active(b)
            msg += "\n\n"
    else:
        msg += "СЕЙЧАС ТЫ НИЧЕГО НЕ ЧИТАЕШЬ 📖\n\n"

    if finished_books:
        msg += "УЖЕ ПРОЧИТАЛ 📚\n"

        for b in finished_books:
            msg += f"*{b['title']}*\n"
            msg += f"{b['author']}\n"
            msg += f"Страниц: {b['total_pages']}\n\n"
    else:
        msg += "ПРОЧИТАННЫХ НЕТ 📚\n"

    bot.send_message(ID, msg, parse_mode="Markdown")
