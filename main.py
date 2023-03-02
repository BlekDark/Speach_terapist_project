import telebot
from telebot import types

from dotenv import load_dotenv

import os
import re

from speach_terapist import get_user_code, add_list_to_google_table, delete_tg_id_for_db
from utils import get_list_name
from user import user_authorization, switch_user, get_users, get_active_user, save_voice_to_google_drive, save_to_google_sheets


load_dotenv()
os.environ
token = os.environ.get("TOKEN")
bot = telebot.TeleBot(token)


# прием сообщения /get_my_id
@bot.message_handler(commands=['get_my_id'])
def get_my_id(message):
    id = message.from_user.id
    bot.send_message(
        message.chat.id, f"Ваш ID - {id}")


# Сообщение /start от логопеда
@bot.message_handler(func=lambda message: str(message.from_user.id) in os.environ.get("SPEECH_TERAPIST_ID") and message.text == "/start")
def start_speech_message(message):
    bot.send_message(
        message.chat.id, "Привествую, можете добавить нового пользователя. Для этого просто напишите ФИО для записи в базу данных")


# прием текстового сообщения от логопеда
@bot.message_handler(func=lambda message: str(message.from_user.id) in os.environ.get("SPEECH_TERAPIST_ID"))
def handle_text(message):
    try:
        full_name = message.text
        code = get_user_code(full_name)
        list_name = get_list_name(full_name, id)
        add_list_to_google_table(list_name)
        print("test1")
        bot.send_message(
            message.chat.id, "Пользьзователь успешно добавлен! Сообщите пользоватлю код регистрации:")
        bot.send_message(
            message.chat.id, code)
        bot.send_message(
            message.chat.id, "его нужно ввести в сообщения бота при регистрации.")
        bot.send_message(
            message.chat.id, f"Домашние задания будут сохраняться в лист {list_name}")
        bot.send_message(
            message.chat.id, "Для добавления нового клиент, введите его ФИО")
    except:
        bot.send_message(
            message.chat.id, f"Неудачная попытка регистрации. Обратитесь к администратору")
    return


#  /delete # где # ид удаляемого (для логопеда)
@bot.message_handler(commands=['delete'], func=lambda message: str(message.from_user.id) in os.environ.get("SPEECH_TERAPIST_ID"))
def command_delete(message):
    try:
        user_id = message.text.split()[1:][0]
        full_name = delete_tg_id_for_db(user_id)
        bot.send_message(
            message.chat.id, f"Пользователь {full_name} удален.")
    except Exception as e:
        bot.send_message(
            message.chat.id, str(e))
    return


# прием сообщения /start от НЕ логопеда (отработает, если предыдущий старт не отработает)
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id, "Приветствую в tg боте нашей клиники. Он создан для записи домашних заданий и отправке их логопеду при помощи готосовых сообщений.")
    bot.send_message(
        message.chat.id, "Для использования введите код, который вам сообщил логопед")


# проверка "Добавить нового пользлвателя"
@bot.message_handler(func=lambda message: message.text == "Добавить нового пользователя")
def check_str_add_new_users(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("Назад")
    markup.add(btn)
    bot.send_message(message.chat.id, "Введите код", reply_markup=markup)


# прием текстового сообщения от НЕ логопеда
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if re.search("^\d+$", message.text):
        try:
            full_name = user_authorization(message.text, message.from_user.id)
            bot.send_message(
                message.chat.id, f"Код корректный. Авторизированный пользователь: {full_name}")
        except Exception as e:
            bot.send_message(
                message.chat.id, str(e))
    else:
        switch_user(message.text, message.from_user.id)
    try:
        users = get_users(message.from_user.id)
    except Exception as e:
        bot.send_message(
            message.chat.id, str(e))
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for user in users:
        if user["enable"] == 1:
            response_message = f"✅ {user['full_name']}"
        else:
            response_message = user['full_name']
        markup.add(types.InlineKeyboardButton(
            text=response_message))
    markup.add(types.InlineKeyboardButton(
        text="Добавить нового пользователя"))
    bot.send_message(
        message.chat.id, "Для отправки домашнего задания запишите голосовое сообщение", reply_markup=markup)
    return


# Прием голосового сообщения
@bot.message_handler(content_types=['voice'])
def voice_processing(message):

    # проверка аутентификации
    try:
        full_name, id = get_active_user(message.from_user.id)
    except Exception as e:
        bot.send_message(
            message.chat.id, str(e))
        return

# гугл драйв
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    list_name = get_list_name(full_name, id)
    link = save_voice_to_google_drive(downloaded_file, list_name)

# сохранение в таблицу
    save_to_google_sheets(link, full_name, id)
    bot.send_message(
        message.chat.id, "Ваше голосовое сообщение сохранено и будет проверенно логопедом в ближайшее время")


if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
