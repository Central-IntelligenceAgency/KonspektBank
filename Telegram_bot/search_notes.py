import telebot
from telebot import types
from text import subjects


def create_keyboard(bot: telebot.TeleBot, message: types.Message):
    keyword_find_notes = types.ReplyKeyboardMarkup(resize_keyboard=True)

    row = []
    for subject in subjects:
        btn = types.KeyboardButton(subjects[subject])
        row.append(btn)
        if len(row) == 6:
            keyword_find_notes.add(*row)
            row = []

    if row:
        keyword_find_notes.add(*row)

    bot.send_message(message.chat.id, "Знание — это сила.\n\nКакой аспект знаний интересует тебя больше всего?\n",
                     reply_markup=keyword_find_notes)