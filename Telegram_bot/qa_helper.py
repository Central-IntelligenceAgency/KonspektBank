import telebot


def qa_helper(bot: telebot.TeleBot, message: telebot.types.Message):
    bot.send_message(message.chat.id, "text", parse_mode="HTML")