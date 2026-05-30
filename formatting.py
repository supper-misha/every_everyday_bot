from telebot import types

INDEX_ID = 0
NAME_ID = 2
DONE_ID = 5

# ROUTIN
def format_routin_tasks(tasks):
    result = '\n'.join([f'✖️ {el[NAME_ID]}' for el in tasks if not el[DONE_ID]])
    if len(result) > 0:
        result += '\n'
    result += '\n'.join([f'☑️ {el[NAME_ID]}' for el in tasks if el[DONE_ID]])
    return result


def markup_for_routin_tasks(list_name, tasks, mode):
    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(el[NAME_ID], callback_data=f'{mode}&{list_name}&{el[INDEX_ID]}') \
               for el in tasks if not el[DONE_ID]]
    markup.row(*buttons)
    return markup, len(buttons)
