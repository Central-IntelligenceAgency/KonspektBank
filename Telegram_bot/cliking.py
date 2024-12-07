import sys
import os
import uuid
import telebot
from telebot import types
from time import sleep
from utils import try_search_files, create_description
from text import *
from Attachments import Photo, Document, Attachment

last_messages: dict[int, telebot.types.Message] = {}  #chatid:last_message
unlimited_users_ids = []
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
    if call.data == 'find_konspekt':
        keyboad_find = types.ReplyKeyboardMarkup(is_persistent=True)

        keyboad_find.add(*get_subject_buttons())

        bot.send_message(call.message.chat.id, "Выбирите предмет", reply_markup=keyboad_find)

        message = get_last_message(call)
        if message.text not in subject_answers_map:
            return
        bot.send_message(call.message.chat.id, "Предмет выбран", reply_markup=types.ReplyKeyboardRemove())
        subject = message.text.split(' ')[0]

        file_paths = try_search_files(subject)

        if not file_paths:
            bot.send_message(call.message.chat.id, "Файлов нету 😭😭")
            return

        for file in file_paths:
            with open(file.file_path, "rb") as files:
                bot.send_document(call.message.chat.id, files, None,
                                  f"Описание: {file.description.get("description")}")
        print("Sent files")

    if call.data == 'find_sum':
        keyboad_find = types.ReplyKeyboardMarkup(resize_keyboard=True)
        row = get_subject_buttons()
        keyboad_find.add(*row)

        bot.send_message(call.message.chat.id, "Выбирите предмет", reply_markup=keyboad_find)

        message = get_last_message(call)
        if message.text not in subject_answers_map:
            return
        subject = message.text.split(' ')[0]
        subjects = len(try_search_files(subject))
        bot.send_message(call.message.chat.id, f"Найдено {subjects} файла(ов)", reply_markup=types.ReplyKeyboardRemove())
        print("sent files count")

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
        row = get_subject_buttons()

        keyword_find_notes.add(*row)

        bot.send_message(call.message.chat.id, "Выбирите нужный вам предмет:",
                         reply_markup=keyword_find_notes)

        message = get_last_message(call)
        if message.text not in subject_answers_map:
            return

        subject = message.text.split(' ')[0]
        bot.send_message(call.message.chat.id, "Предмет выбран", reply_markup=types.ReplyKeyboardRemove())

        with open(f"Files\\{id}-{subject}-{attachment.name}", 'wb') as f:
            f.write(attachment.data)

        description = message.text
        create_description(f"{id}-{attachment.name}", description)

        if call.from_user.id not in upload_limits:
            upload_limits[call.from_user.id] = 1
        else:
            upload_limits[call.from_user.id] += 1

        bot.send_message(call.message.chat.id, "Файл успешно отправлен!")
        print(f"Received file: {attachment.name}, description: {message_description.text}")

    if call.data == 'exit':
        bot.delete_message(call.message.chat.id, call.message.message_id)


def HandleFile(bot: telebot.TeleBot, message: types.Message) -> list[Attachment] | None:
    def check_size(size) -> bool:
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
        if check_size(file.file_size):
            return
        downloaded_file = bot.download_file(file.file_path)
        attachments.append(Photo(downloaded_file, os.path.basename(file.file_path)))

    if message.document:
        document = message.document
        file = bot.get_file(document.file_id)
        if check_size(file.file_size):
            return
        downloaded_file = bot.download_file(file.file_path)
        attachments.append(Document(downloaded_file, os.path.basename(file.file_path)))

    return attachments


def get_last_message(call: types.CallbackQuery):
    old_message = last_messages.get(call.message.chat.id)
    new_message = last_messages.get(call.message.chat.id)
    while old_message == new_message:
        new_message = last_messages.get(call.message.chat.id)
        sleep(1)
    return last_messages[call.message.chat.id]


def get_subject_buttons():
    row = []
    for subject in subject_answers_map:
        btn = types.KeyboardButton(subject)
        row.append(btn)
    return row

