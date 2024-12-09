import threading
from menu import start_menu
from qa_helper import qa_helper
from cliking import callback_query, unlimited_users_updater
from InterfaceUtils import last_messages
from _log import info
import config
import telebot

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start_bot(message: telebot.types.Message):
    threading.Thread(target=start_menu(bot, message.chat.id)).start()


@bot.message_handler(commands=['help'])
def start_helper(message: telebot.types.Message):
    qa_helper(bot, message)


@bot.callback_query_handler(func=lambda call: True)
def callback(call: telebot.types.CallbackQuery):
    threading.Thread(target=lambda: callback_query(call, bot)).start()


@bot.message_handler(content_types=["text", "photo", "document"])
def message_handler(message: telebot.types.Message):
    last_messages[message.chat.id] = message
    info(f"received message: {message.text}")


if __name__ == "__main__":
    threading.Thread(target=unlimited_users_updater).start()
    bot.polling()
