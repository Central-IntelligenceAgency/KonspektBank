import telebot
from telebot import types
from setting import admin, white_list, ban_list


def is_user_admin(user_id):
    return user_id in admin


def admin_menu(bot: telebot.TeleBot, message: types.Message, user_id):
    if is_user_admin(user_id):
        user_name = admin[user_id]

        keyboard = types.InlineKeyboardMarkup()

        btn_add_admin = types.InlineKeyboardButton(text="Список админов", callback_data="admin")
        btn_remove_ban = types.InlineKeyboardButton(text="Баны", callback_data="bans")
        btn_exit = types.InlineKeyboardButton(text="Выйти", callback_data="exit")

        keyboard.add(btn_add_admin)
        keyboard.add(btn_remove_ban)
        keyboard.add(btn_exit)

        bot.send_message(message.chat.id, f"Добро пожаловать, {user_name}!\n\nВы вновь вошли"
                                          f" в святилище знаний, и ваши полномочия как Администратора подтверждены.\n\n"
                                          f"Да будет с вами сила свитков!",
                         reply_markup=keyboard)

    else:
        bot.send_message(message.chat.id, "У вас недостаточно прав, для входа в админ систему ")


def menu_bans(bot: telebot.TeleBot, message: types.Message):
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


def back_admin_menu(bot: telebot.TeleBot, message: types.Message, user_id):
    user_name = admin[user_id]

    kb_back_admin_menu = types.InlineKeyboardMarkup()

    btn_add_admin = types.InlineKeyboardButton(text="Список админов", callback_data="admin")
    btn_remove_ban = types.InlineKeyboardButton(text="Баны", callback_data="bans")
    btn_exit = types.InlineKeyboardButton(text="Выйти", callback_data="exit")

    kb_back_admin_menu.add(btn_add_admin)
    kb_back_admin_menu.add(btn_remove_ban)
    kb_back_admin_menu.add(btn_exit)

    bot.edit_message_text(f"Добро пожаловать, {user_name}!\n\nВы вновь вошли"
                                          f" в святилище знаний, и ваши полномочия как Администратора подтверждены.\n\n"
                                          f"Да будет с вами сила свитков!",
                          chat_id=message.chat.id,
                          message_id=message.message_id,
                          reply_markup=kb_back_admin_menu
                          )


def list_users(bot: telebot.TeleBot, message: types.Message):
    kb_list_users = types.InlineKeyboardMarkup(row_width=3)

    row = []
    for user_id, user_name in white_list.items():
        btn_user = types.InlineKeyboardButton(text=user_name, callback_data=f"add_admin_{user_id}")
        row.append(btn_user)

        if len(row) == 3:
            kb_list_users.add(*row)
            row = []

    if row:
        kb_list_users.add(*row)

    btn_back = types.InlineKeyboardButton(text="Назад", callback_data="back_admin_control")
    kb_list_users.add(btn_back)

    bot.edit_message_text(
        "Ваша воля, стала бы благословением для нового поддоного! Скажите имя, которому позволено обрести "
        "власть над сокровищами знаний.",
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=kb_list_users
    )


def list_admin(bot: telebot.TeleBot, message: types.Message):
    kb_list_admins = types.InlineKeyboardMarkup()

    row = []
    for user_id, user_name in admin.items():
        btn_admin = types.InlineKeyboardButton(text=user_name, callback_data=f"remove_admin_{user_id}")
        row.append(btn_admin)

        if len(row) == 3:
            kb_list_admins.add(*row)
            row = []

    if row:
        kb_list_admins.add(*row)

    btn_back = types.InlineKeyboardButton(text="Назад", callback_data="back_admin_control")
    kb_list_admins.add(btn_back)

    bot.edit_message_text(
        "Выбитите Админы",
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=kb_list_admins
    )


def list_user_ban(bot: telebot.TeleBot, message: types.Message):
    kb_list_user_bans = types.InlineKeyboardMarkup()

    row = []
    for i, (user_id, user_name) in enumerate(ban_list.items()):
        btn_user = types.InlineKeyboardButton(text=user_name, callback_data=str(user_id))
        row.append(btn_user)
        kb_list_user_bans.add(*row)
        row = []
    btn_back = types.InlineKeyboardButton(text="Назад", callback_data="back_admin_control")
    kb_list_user_bans.add(btn_back)

    bot.edit_message_text(
        "Cписок пользователей в бане",
        chat_id=message.chat.id,
        message_id=message.message_id,
        reply_markup=kb_list_user_bans
    )



