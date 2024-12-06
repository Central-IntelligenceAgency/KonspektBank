import threading
from menu import start_menu
from qa_helper import qa_helper
from cliking import callback_query

import telebot

bot = telebot.TeleBot("7666906148:AAG2Q0TUL4RMuv8gQo8DbEuvshkswGm2MlE")


@bot.message_handler(commands=['start'])
def start_bot(message: telebot.types.Message):
    threading.Thread(target=start_menu(bot, message)).start()


@bot.message_handler(commands=['help'])
def start_helper(message: telebot.types.Message):
    qa_helper(bot, message)


@bot.callback_query_handler(func=lambda call: True)
def callback(call: telebot.types.CallbackQuery):
    callback_query(call, bot)


if __name__ == "__main__":
    bot.polling()