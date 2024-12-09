import telebot
from time import sleep
from menu import start_menu
import config
import uuid
from telebot import types

last_messages: dict[int, telebot.types.Message] = {}
waiters = {}

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

    def wait_for_new_message_with_cancel_action(self, text):
        id = str(uuid.uuid4())
        waiters[id] = False
        keyboard_menu = types.InlineKeyboardMarkup()
        keyboard_menu.add(types.InlineKeyboardButton(text=config.cancel_naming, callback_data=f"return+{id}"))

        self.bot.send_message(self.call.message.chat.id, text=text, reply_markup=keyboard_menu)

        old_message = last_messages.get(self.call.message.chat.id)
        new_message = last_messages.get(self.call.message.chat.id)
        while old_message == new_message:
            if new_message == config.cancel_naming:
                del waiters[id]
                return
            if waiters[id]:
                del waiters[id]
                self.bot.delete_message(self.call.message.chat.id, self.call.message.id)
                return
            new_message = last_messages.get(self.call.message.chat.id)
            sleep(0.5)
        del waiters[id]
        return last_messages[self.call.message.chat.id]


    def wait_for_new_message(self):
        old_message = last_messages.get(self.call.message.chat.id)
        new_message = last_messages.get(self.call.message.chat.id)
        while old_message == new_message:
            new_message = last_messages.get(self.call.message.chat.id)
            sleep(0.5)
        return last_messages[self.call.message.chat.id]

    def get_subject(self):
        keyboad = types.ReplyKeyboardMarkup(is_persistent=True)

        keyboad.add(*self.get_subject_buttons())

        self.bot.send_message(self.call.message.chat.id, "Выберите предмет", reply_markup=keyboad)

        message = self.wait_for_new_message()
        if message.text not in self.subjects:
            return
        self.bot.send_message(self.call.message.chat.id, "Предмет выбран", reply_markup=types.ReplyKeyboardRemove())
        return message.text.split(' ')[0]  #предмет

    def get_subject_with_cancel_action(self):
        keyboad = types.ReplyKeyboardMarkup(is_persistent=True)
        btns = self.get_subject_buttons()
        btns.append(types.KeyboardButton(config.cancel_naming))
        keyboad.add(*btns)

        start_message = self.bot.send_message(self.call.message.chat.id, "Выберете предмет", reply_markup=keyboad)

        message = self.wait_for_new_message()

        if message.text == config.cancel_naming:
            message = self.bot.send_message(self.call.message.chat.id, "Отмена", reply_markup=types.ReplyKeyboardRemove())
            self.bot.delete_message(message.chat.id, message.id)
            self.bot.delete_message(start_message.chat.id, start_message.id)
            self.bot.delete_message(self.call.message.chat.id, self.call.message.id)
            start_menu(self.bot, self.call.message.chat.id)
            return
        if message.text not in self.subjects:
            return
        self.bot.send_message(self.call.message.chat.id, "Предмет выбран", reply_markup=types.ReplyKeyboardRemove())
        return message.text.split(' ')[0]  #предмет