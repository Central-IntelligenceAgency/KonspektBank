import json
import os
import uuid
import config
import telebot
from telebot import types
from InterfaceUtils import InterfaceUtils
from time import sleep
from _log import info
from utils import try_search_files, create_description
from text import *
from Attachments import Photo, Document, Attachment

last_messages: dict[int, telebot.types.Message] = {}  # chatid:last_message

if not os.path.exists('unlimited_users.json'):
    unlimited_users_ids = []
    with open('unlimited_users.json', 'w') as f:
        json.dump(unlimited_users_ids, f)
else:
    with open('unlimited_users.json', 'r') as f:
        unlimited_users_ids = json.load(f)

upload_limits = {}

subject_answers_map = {
    "Биология 🔬": biology_replies,
    "Химия 🧪": chemistry_replies,
    "Физика ⚛️": physics_replies,
    "Математика ➕": math_replies,
    "История 📜": history_replies,
    "Иностранный язык 🌍": foreign_language_replies,
    "Обществознание 👥": social_studies_replies,
    "География 🗺️": geography_replies,
    "Экономика 📈": economics_replies,
    "Психология 🧠": psychology_replies,
}


def callback_query(call: types.CallbackQuery, bot: telebot.TeleBot):
    i_utils = InterfaceUtils(bot, call, subject_answers_map)
    if call.data == 'find_konspekt':
        subject = i_utils.get_subject()
        if not subject:
            return
        file_paths = try_search_files(subject)

        if not file_paths:
            bot.send_message(call.message.chat.id, "Файлов нету 😭😭")
            return

        for file in file_paths:
            with open(file.file_path, "rb") as files:
                bot.send_document(call.message.chat.id, files, None,
                                  f"Описание: {file.description.get("description")}")
        info(f"Sent files to {call.from_user.username}")

    if call.data == 'find_sum':
        subject = i_utils.get_subject()
        subjects = len(try_search_files(subject))
        bot.send_message(call.message.chat.id, f"Найдено {subjects} файла(ов)",
                         reply_markup=types.ReplyKeyboardRemove())
        info(f"Sent files count to {call.from_user.username}")

    if call.data == "add_file":
        if call.from_user.id in upload_limits and call.from_user.id not in unlimited_users_ids:
            if upload_limits[call.from_user.id] >= 3:
                bot.send_message(call.message.chat.id, "Вы превысили лимит на день!")
                return
        id = f"{uuid.uuid4()}".replace("-", "+")
        bot.send_message(call.message.chat.id, "Отправьте файл:")

        message = i_utils.wait_for_new_message()

        attachment = HandleFile(bot, message)[0]

        bot.send_message(call.message.chat.id, "Отправьте описание:")
        message_description = i_utils.wait_for_new_message()

        subject = i_utils.get_subject()

        with open(f"Files/{id}-{subject}-{attachment.name}", 'wb') as f:
            f.write(attachment.data)

        description = message_description.text
        create_description(f"{id}-{attachment.name}", description)

        if call.from_user.id not in upload_limits:
            upload_limits[call.from_user.id] = 1
        else:
            upload_limits[call.from_user.id] += 1

        bot.send_message(call.message.chat.id, "Файл успешно отправлен!")
        info(
            f"Received file: {attachment.name}, description: {message_description.text}, from {call.from_user.username}")
    if call.data == 'exit':
        bot.delete_message(call.message.chat.id, call.message.message_id)


def HandleFile(bot: telebot.TeleBot, message: types.Message) -> list[Attachment] | None:
    def check_size(size) -> bool:
        if not size:
            return False
        if message.from_user.id in unlimited_users_ids:
            if size / 1024 / 1024 > 500:
                bot.send_message(message.chat.id, "файл слишком большой, он не может быть загружен")
                return False
            return True
        if size / 1024 / 1024 > 100:
            bot.send_message(message.chat.id, "файл слишком большой, он не может быть загружен")
            return False
        return True

    attachments = []
    if message.photo:
        photo = message.photo[-1]
        file = bot.get_file(photo.file_id)
        if not check_size(file.file_size):
            info("size limit reached")
            return
        downloaded_file = bot.download_file(file.file_path)
        attachments.append(Photo(downloaded_file, os.path.basename(file.file_path)))

    if message.document:
        document = message.document
        file = bot.get_file(document.file_id)
        if not check_size(file.file_size):
            info("size limit reached")
            return
        downloaded_file = bot.download_file(file.file_path)
        attachments.append(Document(downloaded_file, os.path.basename(file.file_path)))

    return attachments


def unlimited_users_updater():
    global unlimited_users_ids
    while True:
        sleep(config.unlimited_users_updater_sleep_time)
        if not os.path.exists('unlimited_users.json'):
            unlimited_users_ids = []
            with open('unlimited_users.json', 'w') as f:
                json.dump(unlimited_users_ids, f)
        else:
            with open('unlimited_users.json', 'r') as f:
                unlimited_users_ids = json.load(f)
