import telebot
from telebot import types
from text import subjects


def add_file(bot: telebot.TeleBot, message: telebot.types.Message):
    bot.send_message(message.chat.id, "Добавить файл")
    #Добавление файла
    bot.send_message(message.chat.id, "Описание")
    #Создание описания

    keyword_add_file = types.ReplyKeyboardMarkup(resize_keyboard=True)

    row = []
    for subject in subjects:
        btn = types.KeyboardButton(subjects[subject])
        row.append(btn)
        if len(row) == 6:
            keyword_add_file.add(*row)
            row = []

    bot.send_message(message.chat.id, "Выбирите предмет", reply_markup=keyword_add_file)