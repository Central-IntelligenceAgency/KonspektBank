import threading
from menu import start_menu
from qa_helper import qa_helper
from cliking import callback_query, upload_limits_updater
from InterfaceUtils import last_messages
from _log import info
import admin
import config
import telebot


bot = telebot.TeleBot(config.token)


def is_user_allowed(user_id):
    return user_id in config.white_list


def is_user_banned(user_id):
    return config.ban_list.get(user_id, None)


@bot.message_handler(commands=['start'])
def start_bot(message: telebot.types.Message):
    user_id = message.chat.id

    if is_user_allowed(user_id):
        user_name = config.white_list[user_id]
        bot.send_message(message.chat.id, f"Здравствуйте, {user_name}!")
        threading.Thread(target=start_menu, args=(bot, message.chat.id)).start()

    elif is_user_banned(user_id):
        reason_ban = config.ban_list[user_id]
        bot.send_message(message.chat.id, f"Внимание!\n\n На вашем аккаунте обнаружен бан.\n\n Причина:\n"
                                          f"{reason_ban}")
        return

    else:
        bot.send_message(message.chat.id, "Вы не можете использовать этого бота.")


@bot.message_handler(commands=['help'])
def start_helper(message: telebot.types.Message):
    qa_helper(bot, message)


@bot.message_handler(commands=['admin'])
def start_helper(message: telebot.types.Message):
    print(message.chat.id)
    admin.admin_menu(bot, message, message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def callback(call: telebot.types.CallbackQuery):
    threading.Thread(target=lambda: callback_query(call, bot)).start()


@bot.message_handler(content_types=["text", "photo", "document"])
def message_handler(message: telebot.types.Message):
    last_messages[message.chat.id] = message
    info(f"received message: {message.text}")


if __name__ == "__main__":
    threading.Thread(target=admin.updater).start()
    threading.Thread(target=upload_limits_updater).start()
    bot.infinity_polling()
