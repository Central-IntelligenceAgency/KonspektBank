import sys
import os
import telebot

sys.path.append(os.path.abspath('../KonspektBank'))

from telebot import types
from search_notes import create_keyboard
from KonspektBank import GeminiModule  # Импортируем модуль
from KonspektBank.utils import try_search_files, create_description
from text import *
from Attachments import Photo, Document, Attachment


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
        file_paths = try_search_files(subject.split(' ')[0])
        for file in file_paths:
            with open(file.file_path, "rb") as files:
                bot.send_document(call.message.chat.id, files, None,
                                  f"Описание: {file.description["description"]}")
        if not file_paths:
            bot.send_message(call.message.chat.id, "Файла нету (")

    if call.data == 'find_sum':
        pass

    if call.data == "add_file":
        bot.send_message(call.message.chat.id, "Отправте файл:")
        attachment = HandleFile(bot, call)[0]
        with open(f"{attachment.name}", 'wb') as f:
            f.write(attachment.data)
        bot.send_message(call.message.chat.id, "Отправьте описание:")
        process_description(bot, call, attachment)
        #тогда адиос
        #you too
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

        bot.send_message(call.message.chat.id, "Выбирите нужный вам предмет:",
                         reply_markup=keyword_find_notes)

    if call.data == 'exit':
        bot.delete_message(call.message.chat.id, call.message.message_id)


def HandleFile(bot: telebot.TeleBot, call: types.CallbackQuery) -> list[Attachment] | None:
    attachments = []
    if call.message.photo:
        photo = call.message.photo[-1]
        file = bot.get_file(photo.file_id)
        if file.file_size / 1024 / 1024 > 100:
            return
        downloaded_file = bot.download_file(file.file_path)
        attachments.append(Photo(downloaded_file, file.file_path))

    if call.message.document:
        document = call.message.document
        file = bot.get_file(document.file_id)
        if file.file_size / 1024 / 1024 > 100:
            return
        downloaded_file = bot.download_file(file.file_path)
        attachments.append(Document(downloaded_file, file.file_path))

    return attachments


def process_description(bot: telebot.TeleBot, call: types.CallbackQuery, attachment:Attachment):
    description = call.message.text
    create_description(f"Files\\{attachment.name}", description)
    bot.send_message(call.message.chat.id, "Описание добавленно")



