import telebot
from time import sleep
from telebot import types

last_messages: dict[int, telebot.types.Message] = {}


class InterfaceUtils():  # чтобы не передавать 100000 аргументов
    def __init__(self, bot: telebot.TeleBot, call: types.CallbackQuery, subjects: dict):
        self.bot = bot
        self.call = call
        self.subjects = subjects

    def get_subject_buttons(self):
        row = []
        for subject in self.subjects:
            btn = types.KeyboardButton(subject)
            row.append(btn)
        return row

    def wait_for_new_message(self):
        old_message = last_messages.get(self.call.message.chat.id)
        new_message = last_messages.get(self.call.message.chat.id)
        while old_message == new_message:
            new_message = last_messages.get(self.call.message.chat.id)
            sleep(1)
        return last_messages[self.call.message.chat.id]

    def get_subject(self):
        keyboad_find = types.ReplyKeyboardMarkup(is_persistent=True)

        keyboad_find.add(*self.get_subject_buttons())

        self.bot.send_message(self.call.message.chat.id, "Выберите предмет", reply_markup=keyboad_find)

        message = self.wait_for_new_message()
        if message.text not in self.subjects:
            return
        self.bot.send_message(self.call.message.chat.id, "Предмет выбран", reply_markup=types.ReplyKeyboardRemove())
        return message.text.split(' ')[0]  #предмет
