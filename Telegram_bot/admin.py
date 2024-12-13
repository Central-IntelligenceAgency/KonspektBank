import os.path
import json
import telebot
from telebot import types
import config
import time


def is_user_admin(user_id):
    return user_id in admins

def admin_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    btn_add_admin = types.InlineKeyboardButton(text="Список админов", callback_data="admin")
    btn_remove_ban = types.InlineKeyboardButton(text="Баны", callback_data="bans")
    btn_exit = types.InlineKeyboardButton(text="Выйти", callback_data="exit")

    keyboard.add(btn_add_admin)
    keyboard.add(btn_remove_ban)
    keyboard.add(btn_exit)

    return keyboard

def users_list(user_button_callback, return_button_callback, list):
    users_keyboard = types.InlineKeyboardMarkup(row_width=3)

    row = []
    for user_id, user_name in list.items():
        btn_user = types.InlineKeyboardButton(text=user_name, callback_data=f"{user_button_callback}_{user_id}")
        row.append(btn_user)

        if len(row) == 3:
            users_keyboard.add(*row)
            row = []

    if row:
        users_keyboard.add(*row)

    btn_back = types.InlineKeyboardButton(text="Назад", callback_data=f"{return_button_callback}")
    users_keyboard.add(btn_back)
    return users_keyboard

def admin_menu(bot: telebot.TeleBot, message: types.Message, user_id, edit=False):
    if not is_user_admin(user_id):
        bot.send_message(message.chat.id, "У вас недостаточно прав, для входа в админ систему")
        return

    user_name = admins[user_id]

    keyboard = admin_keyboard()
    if not edit:
        bot.send_message(message.chat.id, f"Добро пожаловать, {user_name}!\n\nВы вновь вошли"
                                          f" в святилище знаний, и ваши полномочия как Администратора подтверждены.\n\n"
                                          f"Да будет с вами сила свитков!",
                         reply_markup=keyboard)
    else:
        bot.edit_message_text(f"Добро пожаловать, {user_name}!\n\nВы вновь вошли"
                              f" в святилище знаний, и ваши полномочия как Администратора подтверждены.\n\n"
                              f"Да будет с вами сила свитков!",
                              chat_id=message.chat.id,
                              message_id=message.message_id,
                              reply_markup=keyboard
                              )


def menu_bans(bot: telebot.TeleBot, message: types.Message):
    if not is_user_admin(message.chat.id):
        bot.send_message(message.chat.id, "У вас недостаточно прав, для входа в админ систему")
        return

    keyboard_bans = types.InlineKeyboardMarkup()

    btn_add_ban = types.InlineKeyboardButton(text="Выдать бан", callback_data="ban")
    btn_remove_ban = types.InlineKeyboardButton(text="Убрать бан", callback_data="remove_ban")
    btn_back = types.InlineKeyboardButton(text="Назад", callback_data="back")

    keyboard_bans.add(btn_add_ban)
    keyboard_bans.add(btn_remove_ban)
    keyboard_bans.add(btn_back)

    bot.edit_message_text(
        "Выбирите нужный вам пункт",
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=keyboard_bans
    )


def admin_control(bot: telebot.TeleBot, message: types.Message):
    if not is_user_admin(message.chat.id):
        bot.send_message(message.chat.id, "У вас недостаточно прав, для входа в админ систему")
        return

    keyboard_admin_control = types.InlineKeyboardMarkup()

    btn_add_admin = types.InlineKeyboardButton(text="Выдать админку", callback_data="add_admin")
    btn_remove_admin = types.InlineKeyboardButton(text="Убрать админку", callback_data="remove_admin")
    btn_back = types.InlineKeyboardButton(text="Назад", callback_data="back")

    keyboard_admin_control.add(btn_add_admin)
    keyboard_admin_control.add(btn_remove_admin)
    keyboard_admin_control.add(btn_back)

    bot.edit_message_text(
        "А теперь, великий повелитель знаний, взгляните на высших подданных.\n\nВыберите из них тех, кто достоин"
        "носить титул администратора. А кому суждено его лишиться",
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=keyboard_admin_control
    )


def list_users(bot: telebot.TeleBot, message: types.Message, callback, return_callback):
    if not is_user_admin(message.chat.id):
        bot.send_message(message.chat.id, "У вас недостаточно прав, для входа в админ систему")
        return

    kb_list_users = users_list(callback, return_callback, white_list)

    bot.edit_message_text(
        "Ваша воля, стала бы благословением для нового поддоного! Скажите имя, которому позволено обрести "
        "власть над сокровищами знаний.",
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=kb_list_users
    )


def list_admin(bot: telebot.TeleBot, message: types.Message, callback=""):
    if not is_user_admin(message.chat.id):
        bot.send_message(message.chat.id, "У вас недостаточно прав, для входа в админ систему")
        return

    kb_list_admins = users_list(callback, "back_admin_control", config.admins)

    bot.edit_message_text(
        "Выбитите Админы",
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=kb_list_admins
    )


def list_user_ban(bot: telebot.TeleBot, message: types.Message):
    if not is_user_admin(message.chat.id):
        bot.send_message(message.chat.id, "У вас недостаточно прав, для входа в админ систему")
        return

    kb_list_user_bans = users_list("back_admin_control", "back_from_bans", ban_list)

    bot.edit_message_text(
        "Cписок пользователей в бане",
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=kb_list_user_bans
    )


def updater():
    global admins
    global white_list
    global ban_list
    def rewrite_keys_to_int(dict):
        keys = list(dict.keys())
        for key in keys:
            value = dict[key]
            dict.pop(key)
            dict[int(key)] = value
        return dict

    while True:
        if not os.path.exists(config.white_list_path):
            with open(config.white_list_path, 'w', encoding="utf-8") as f:
                f.write(json.dumps(white_list, indent=4, sort_keys=True))

        if not os.path.exists(config.ban_list_path):
            with open(config.ban_list_path, 'w', encoding="utf-8") as f:
                f.write(json.dumps(ban_list, indent=4, sort_keys=True))

        if not os.path.exists(config.admins_list_path):
            with open(config.admins_list_path, 'w', encoding="utf-8") as f:
                f.write(json.dumps(admins, indent=4, sort_keys=True))

        with open(config.admins_list_path, 'r', encoding="utf-8") as f:
            admins = rewrite_keys_to_int(json.load(f))

        with open(config.white_list_path, 'r', encoding="utf-8") as f:
            white_list = rewrite_keys_to_int(json.load(f))

        with open(config.ban_list_path, 'r', encoding="utf-8") as f:
            ban_list = rewrite_keys_to_int(json.load(f))

        time.sleep(60)
