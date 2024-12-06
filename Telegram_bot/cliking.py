import sys
import os
import telebot

sys.path.append(os.path.abspath('../KonspektBank'))

from telebot import types
from search_notes import create_keyboard
from KonspektBank import GeminiModule  # Импортируем модуль
from KonspektBank.utils import try_search_files, try_generate_description_for_file
from text import *


def callback_query(call: types.CallbackQuery, bot: telebot.TeleBot):
    subject = call.data
    subject_file_map = {
        "Биология 🔬": biology_replies,
        "Химия 🧪": chemistry_replies,
        "Физика ⚛️": physics_replies,
        "Математика ➕": math_replies,
        "История 📜": history_replies,
        "Иностранный язык 🌍": foreign_language_replies,
        "Обществознание 👥": social_studies_replies,
        "География 🗺️": geography_replies,
        "Экономика": economics_replies,
        "Психология": psychology_replies,
    }

    if call.data == 'find_konspekt':
        create_keyboard(bot, call.message)

    if call.data == 'find_sum':
        file_paths = try_search_files(subject.split(' ')[0])
        for file in file_paths:
            with open(file.file_path, "rb") as files:
                bot.send_document(call.message.chat.id, files, None,
                                  f"Описание: {file.description["description"]}")
        if not file_paths:
            bot.send_message(call.message.chat.id, "Файла нету (")

    if call.data == "add_file":
        bot.send_message("")


    if call.data == 'exit':
        bot.delete_message(call.message.chat.id, call.message.message_id)

    if subject in subject_file_map:
        file_paths = try_search_files(subject.split(' ')[0])

        if file_paths:
            bot.send_message(call.message.chat.id, f"Вот конспекты по {subject}:\n")
            bot.send_photo()

            response_text = subject_file_map[subject][0]
            bot.send_message(call.message.chat.id, response_text)
        else:
            bot.send_message(call.message.chat.id, f"К сожалению, конспекты по {subject} не найдены.")