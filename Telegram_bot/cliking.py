import sys
import os
import telebot

from telebot import types
from search_notes import create_keyboard
from KonspektBank import GeminiModule  # Импортируем модуль
from KonspektBank.utils import try_search_file, try_generate_description_for_file
from text import *

sys.path.append(os.path.abspath('../KonspektBank'))


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
        pass

    if call.data == 'exit':
        bot.delete_message(call.message.chat.id, call.message.message_id)

    if subject in subject_file_map:
        file_path = try_search_file(subject.split(' ')[0])

        if file_path:
            description = try_generate_description_for_file(file_path)

            bot.send_message(call.message.chat.id, f"Вот конспекты по {subject}:\n{file_path}")

            response_text = subject_file_map[subject][0]
            bot.send_message(call.message.chat.id, response_text)
        else:
            bot.send_message(call.message.chat.id, f"К сожалению, конспекты по {subject} не найдены.")