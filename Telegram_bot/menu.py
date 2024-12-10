import telebot
from telebot import types


def start_menu(bot: telebot.TeleBot, channel_id):
    keyboard_menu = types.InlineKeyboardMarkup()

    btn_find_konspekt = types.InlineKeyboardButton(text="🔎 Найти конспекты", callback_data="find_konspekt")
    btn_fing_sum = types.InlineKeyboardButton(text="📂 Найти количество конспектов", callback_data="find_sum")
    btn_add_file = types.InlineKeyboardButton(text="➕ Добавить файл", callback_data="add_file")

    keyboard_menu.add(btn_find_konspekt)
    keyboard_menu.add(btn_fing_sum)
    keyboard_menu.add(btn_add_file)

    bot.send_message(channel_id, text="Приветствую тебя, мой ученик. Я — Страж Данных\n\n"
                                      "Скажи мне, какой вопрос терзает твой разум?"
                                       "Я здесь, чтобы предоставить ответы.",
                                       reply_markup=keyboard_menu)