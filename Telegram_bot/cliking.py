import os
import uuid
from InterfaceUtils import InterfaceUtils, waiters
from _log import info
from utils import try_search_files, create_description
from menu import start_menu
from telebot import types
from text import *
from Attachments import Photo, Document, Attachment
import admin
import telebot
import config
import math

upload_limits = {}

subject_answers_map = {
    "Биология 🔬": biology_replies,
    "Химия 🧪": chemistry_replies,
    "Физика ⚛️": physics_replies,
    "Математика ✏": math_replies,
    "История 📜": history_replies,
    "Иностранный язык 🌍": foreign_language_replies,
    "Обществознание 👥": social_studies_replies,
    "География 🗺️": geography_replies,
    "Экономика 📈": economics_replies,
    "Психология 🧠": psychology_replies,
}

page_db = {} #id:page
return_keyboard = types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text=config.cancel_naming, callback_data=f"back_to_menu")]])

def find_konspekt(i_utils, call, bot, subject=None):
    if not subject:
        subject = i_utils.get_subject_with_cancel_action()
        if not subject:
            return
    file_paths = try_search_files(subject)
    max_pages = int(math.ceil(len(file_paths) / config.page_step))
    current_page_files = file_paths[page_db[call.message.chat.id]:page_db[call.message.chat.id] + config.page_step]
    current_page = int(math.ceil((page_db[call.message.chat.id]+config.page_step) / config.page_step))
    print(current_page)
    if not current_page_files:
        bot.send_message(call.message.chat.id, "Файлов нету 😭😭", reply_markup=return_keyboard)
        return
    bot.send_message(call.message.chat.id, f"Вот файлы по {subject}:")
    for i, file in enumerate(current_page_files):
        with open(file.file_path, "rb") as files:
            bot.send_document(call.message.chat.id, files, None,
                              f"Файл {i+1}; Описание: {file.description.get("description")}")
    keyboard = types.InlineKeyboardMarkup([[
                         types.InlineKeyboardButton(text=f"✏ Задать свою страницу",
                                                    callback_data=f"set_page+{call.message.chat.id}+{subject}"),
                         types.InlineKeyboardButton(text=f"↩ Вернуться к меню",
                                                    callback_data=f"back_to_menu")

                     ]], row_width=8)
    if max_pages > 1 and current_page < max_pages:
        keyboard.add(types.InlineKeyboardButton(text=f"▶ Следующая",
                                                    callback_data=f"next_page+{call.message.chat.id}+{subject}"),)
    bot.send_message(call.message.chat.id, f"\nСтраница {current_page}/{max_pages}",
                     reply_markup=keyboard)

    info(f"Sent files to {call.from_user.username}")

def callback_query(call: types.CallbackQuery, bot: telebot.TeleBot):

    i_utils = InterfaceUtils(bot, call, subject_answers_map)
    if call.data == 'find_konspekt':
        page_db[call.message.chat.id] = 0
        find_konspekt(i_utils, call, bot)

    if call.data == "back_to_menu":
        bot.delete_message(call.message.chat.id, call.message.id)
        start_menu(bot, call.message.chat.id)

    if "set_page" in call.data:
        subject = call.data.split("+")[2]

        file_paths = try_search_files(subject)
        max_pages = int(math.ceil(len(file_paths)+config.page_step / config.page_step))
        print(max_pages)

        bot.delete_message(call.message.chat.id, call.message.id)
        id = int(call.data.split("+")[1])
        message = i_utils.wait_for_new_message_with_cancel_action("Отправьте номер:")

        if not message.text:
            return
        try:
            if id in page_db:
                print(int(message.text))
                page_db[id] = (config.page_step * int(message.text)) - config.page_step
        except:
            return
        current_page = int(math.ceil((page_db[call.message.chat.id]) / config.page_step))
        print(current_page)
        if current_page > max_pages:
            page_db[id] = 0

        find_konspekt(i_utils, call, bot, subject) # send files

    if "next_page" in call.data:
        bot.delete_message(call.message.chat.id, call.message.id)
        id = int(call.data.split("+")[1])
        if id in page_db:
            page_db[id] += config.page_step # + 1 page
        find_konspekt(i_utils, call, bot, call.data.split("+")[2]) # send files

    if call.data == 'find_sum':
        subject = i_utils.get_subject_with_cancel_action()

        subjects = len(try_search_files(subject))
        bot.send_message(call.message.chat.id, f"Найдено {subjects} файла(ов)",
                         reply_markup=types.ReplyKeyboardRemove())
        info(f"Sent files count to {call.from_user.username}")

    if call.data == "add_file":
        if call.from_user.id in upload_limits and not admin.is_user_admin(call.message.chat.id):
            if upload_limits[call.from_user.id] >= 3:
                bot.send_message(call.message.chat.id, "Вы превысили лимит на день!", reply_markup=return_keyboard)
                return
        id = f"{uuid.uuid4()}".replace("-", "+")

        message = i_utils.wait_for_new_message_with_cancel_action("Отправьте файл:")

        if not message:
            return

        attachments = HandleFile(bot, message)
        if not attachments:
            return
        attachment = attachments[0]

        message_description = i_utils.wait_for_new_message_with_cancel_action("Отправьте описание:")

        if not message_description:
            return

        subject = i_utils.get_subject_with_cancel_action()

        if not subject:
            return

        with open(f"Files/{id}-{subject}-{attachment.name}", 'wb') as f:
            f.write(attachment.data)

        description = message_description.text
        if not description:
            return
        create_description(f"{id}-{attachment.name}", description)

        if call.from_user.id not in upload_limits:
            upload_limits[call.from_user.id] = 1
        else:
            upload_limits[call.from_user.id] += 1

        bot.send_message(call.message.chat.id, "Файл успешно отправлен!", reply_markup=return_keyboard)
        info(
            f"Received file: {attachment.name}, description: {message_description.text}, from {call.from_user.username}")
    if "return" in call.data:
        bot.delete_message(call.message.chat.id, call.message.id)
        start_menu(bot, call.message.chat.id)
        if call.data.split("+")[1] in waiters:
            waiters[call.data.split("+")[1]] = True

    if call.data == "admin":
        admin.admin_control(bot, call.message)

    if call.data == "bans":
        admin.menu_bans(bot, call.message)

    if call.data == "back":
        admin.admin_menu(bot, call.message, call.message.chat.id, edit=True)

    if call.data == "add_admin":
        admin.list_users(bot, call.message, "add_admin", "back_admin_control")

    if call.data == "remove_admin":
        admin.list_admin(bot, call.message, "remove_admin")

    if call.data == "back_admin_control":
        admin.admin_control(bot, call.message)

    if call.data == "back_from_bans":
        admin.menu_bans(bot, call.message)

    if call.data == "ban":
        admin.list_users(bot, call.message, "ban1", "back_from_bans")

    if call.data == "remove_ban":
        admin.list_user_ban(bot, call.message)

    if call.data == "exit":
        bot.delete_message(call.message.chat.id, call.message.id)

    if call.data.startswith("add_admin_"):
        user_id = int(call.data.split("_")[2])
        user_name = config.white_list.get(user_id)

        if user_name:
            if user_id in config.admins:
                bot.answer_callback_query(call.id, text=f"{user_name} уже является администратором!")
            else:
                config.admins[user_id] = user_name
                bot.answer_callback_query(call.id, text=f"{user_name} добавлен в список администраторов!")

            admin.list_admin(bot, call.message)
        return

    if call.data.startswith("remove_admin_"):
        user_id = int(call.data.split("_")[2])
        user_name = config.white_list.get(user_id)

        if user_name:
            del config.admins[user_id]
            bot.answer_callback_query(call.id, text=f"{user_name} удалён из списка администраторов!")
            admin.list_admin(bot, call.message)
        return


def HandleFile(bot: telebot.TeleBot, message: types.Message) -> list[Attachment] | None:
    def check_size(size) -> bool:
        if not size:
            return False
        if admin.is_user_admin(message.chat.id):
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
