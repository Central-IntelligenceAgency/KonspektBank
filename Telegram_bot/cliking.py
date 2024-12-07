import sys
import os
import uuid
import telebot

sys.path.append(os.path.abspath('../KonspektBank'))
from typing import Any
from telebot import types
#from search_notes import create_keyboard
from KonspektBank import GeminiModule  # Импортируем модуль
from time import sleep
from KonspektBank.utils import try_search_files, create_description
from text import *
from Attachments import Photo, Document, Attachment

last_messages:dict[int, telebot.types.Message] = {} #chatid:last_message
unlimited_users_ids = []
upload_limits = {}

def callback_query(call: types.CallbackQuery, bot: telebot.TeleBot):
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
        flag = True
        keyboad_find = types.ReplyKeyboardMarkup(resize_keyboard=flag)
        bot.send_message(call.message.chat.id, "Выбирите предмет", reply_markup=keyboad_find)

        row = get_buttons()
        keyboad_find.add(*row)

        message = get_last_message(call)
        if message.text not in subject_file_map:
            return
        subject = message.text.split(' ')[0]

        file_paths = try_search_files(subject)

        if not file_paths:
            bot.send_message(call.message.chat.id, "Файлов нету 😭😭")
            return

        for file in file_paths:
            with open(file.file_path, "rb") as files:
                bot.send_document(call.message.chat.id, files, None,
                                  f"Описание: {file.description.get("description")}")
        flag = False
        print("Sent files")


    if call.data == 'find_sum':
        pass

    if call.data == "add_file":
        if call.from_user.id in upload_limits and call.from_user.id not in unlimited_users_ids:
            if upload_limits[call.from_user.id] >= 3:
                bot.send_message(call.message.chat.id, "Вы привысили лимит на день!:")
                return
        id = f"{uuid.uuid4()}".replace("-", "+")
        bot.send_message(call.message.chat.id, "Отправте файл:")

        message = get_last_message(call)

        attachment = HandleFile(bot, message)[0]

        bot.send_message(call.message.chat.id, "Отправьте описание:")
        message_description = get_last_message(call)

        keyword_find_notes = types.ReplyKeyboardMarkup(resize_keyboard=True)
        row = get_buttons()

        if row:
            keyword_find_notes.add(*row)

        bot.send_message(call.message.chat.id, "Выбирите нужный вам предмет:",
                         reply_markup=keyword_find_notes)

        message = get_last_message(call)
        if message.text not in subject_file_map:
            return
        subject = message.text.split(' ')[0]
        with open(f"Files\\{id}-{subject}-{attachment.name}", 'wb') as f:
            f.write(attachment.data)
        process_description(bot, message_description, attachment, id)

        if call.from_user.id not in upload_limits:
            upload_limits[call.from_user.id] = 1
        else:
            upload_limits[call.from_user.id] += 1

        bot.send_message(call.message.chat.id, "Файл успешно отправлен!")
        print(f"Received file: {attachment.name}, description: {message_description.text}")

    if call.data == 'exit':
        bot.delete_message(call.message.chat.id, call.message.message_id)


def HandleFile(bot: telebot.TeleBot, message: types.Message) -> list[Attachment] | None:
    attachments = []
    if message.photo:
        photo = message.photo[-1]
        file = bot.get_file(photo.file_id)
        if file.file_size / 1024 / 1024 > 100:
            return
        downloaded_file = bot.download_file(file.file_path)
        attachments.append(Photo(downloaded_file, os.path.basename(file.file_path)))

    if message.document:
        document = message.document
        file = bot.get_file(document.file_id)
        if file.file_size / 1024 / 1024 > 100:
            return
        downloaded_file = bot.download_file(file.file_path)
        attachments.append(Document(downloaded_file, os.path.basename(file.file_path)))

    return attachments


def process_description(bot: telebot.TeleBot, message: types.Message, attachment:Attachment, id):
    description = message.text
    create_description(f"{id}-{attachment.name}", description)
    bot.send_message(message.chat.id, "Описание добавленно")


def get_last_message(call: types.CallbackQuery):
    old_message = last_messages.get(call.message.chat.id)
    new_message = last_messages.get(call.message.chat.id)
    while old_message == new_message:
        new_message = last_messages.get(call.message.chat.id)
        sleep(1)
    return last_messages[call.message.chat.id]


def get_buttons():
    row = []
    for subject in subjects:
        btn = types.KeyboardButton(subjects[subject])
        row.append(btn)
        if len(row) == 6:
            row = []
    return row
