import os
from os.path import join, dirname
from dotenv import load_dotenv
import json
import re
import requests
import telebot
from flask import Flask, request

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

server = Flask(__name__)

bot = telebot.TeleBot(os.environ.get('TELEBOT_TOKEN'))
bot.set_webhook(url=os.environ.get('PAPICH_NGROK_URL'))

API_URL = 'http://127.0.0.1:8000/'
MEDIA_CONTENT_ROOT = 'media_content/'


@server.route('/', methods=["POST"])
def webhook():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]
    )
    return "ok"


@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    if get_current_user(message) is None:
        return
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     'Приветствую, жалкий кожаный мешок! Я, PapichBot, окончил 8 классов и уполномочен познакомить '
                     'необразованное человечество с творчеством Величайшего. Отправь /media_content_index чтобы '
                     'вывести список доступных фраз Величайшего или /media_content_new чтобы залить свой медиаконтент '
                     'связанный с Величайшим.', reply_markup=get_default_keyboard())


@bot.message_handler(commands=['media_content_new'])
def media_content_new(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Выбери имя для загружаемого контента. Лучше что нибудь читаемое.')
    bot.register_next_step_handler(message, media_content_create1)


def media_content_create1(message):
    try:
        chat_id = message.chat.id
        media_content_displayed_name = message.text
        if media_content_displayed_name is None or media_content_displayed_name == '':
            raise Exception
        bot.send_message(chat_id, 'Ну давай, скидывай свой контент. Поддерживается аудио в форматах mp3, ogg и wav.')
        bot.register_next_step_handler(message, media_content_create2, media_content_displayed_name)
    except Exception:
        bot.send_message(chat_id, "У тебя там 0 iq что ли? Присылать можно только аудио файлы в форматах .mp3, "
                                  ".ogg и .wav")


def media_content_create2(message, media_content_displayed_name):
    curr_user = get_current_user(message)
    if curr_user is None:
        return
    chat_id = message.chat.id
    try:
        if not re.match(r'audio/mpeg|audio/vnd\.wav|audio/ogg', message.audio.mime_type):
            raise Exception

        file_info = bot.get_file(message.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        media_content_path = 'audio/' + file_info.file_unique_id + '.' + file_info.file_path.split('.')[-1]
        with open(MEDIA_CONTENT_ROOT + media_content_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        obj_data = {'displayed_name': media_content_displayed_name, 'filepath': media_content_path,
                    'author': curr_user['external_id']}
        received_response = requests.post(API_URL + 'media_content/', data=obj_data)

        bot.send_message(chat_id, "Ну все, готово. Твой контент доступен в общем списке")
    except Exception as e:
        bot.send_message(chat_id, "У тебя там 0 iq что ли? Присылать можно только аудио файлы в форматах .mp3, "
                                  ".ogg и .wav")


@bot.message_handler(commands=['media_content_index'])
def media_content_index(message):
    if get_current_user(message) is None:
        return
    chat_id = message.chat.id

    message_text = "А вот и список доступных фраз Калыча:\n"
    markup = get_media_content_keyboard()
    bot.send_message(chat_id, message_text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: re.match(r'/media_content_show_\d+', call.data))
def media_content_show(call):
    chat_id = call.message.chat.id
    requested_id = re.search(r'/media_content_show_\d+', call.data).group().split('_')[3]
    content_data = json.loads(requests.get(API_URL + 'media_content/' + requested_id).content)

    if 'status_code' in content_data and content_data['status_code'] == 404:
        bot.send_message(chat_id, 'Нет такой фразы', reply_markup=get_default_keyboard())
    else:
        bot.send_message(chat_id, f"Отправляю {content_data['displayed_name']}...", reply_markup=get_default_keyboard())
        media_content = open(MEDIA_CONTENT_ROOT + content_data['filepath'], 'rb')
        bot.send_audio(chat_id, media_content)


@bot.callback_query_handler(func=lambda call: re.match(r'/media_content_like_\d+', call.data))
def media_content_show(call):
    chat_id = call.message.chat.id
    requested_id = re.search(r'/media_content_like_\d+', call.data).group().split('_')[3]
    content_data = json.loads(requests.get(API_URL + 'media_content/' + requested_id).content)

    if 'status_code' in content_data and content_data['status_code'] == 404:
        return

    headers = {'content-type': 'application/json'}
    if call.from_user.id in content_data['likers']:
        obj_data = {'likers': [{'external_id': str(call.from_user.id)}]}
        response = requests.delete(API_URL + 'media_content/' + requested_id + '/remove_likers/',
                                   data=json.dumps(obj_data), headers=headers)
    else:
        obj_data = {'likers': [str(call.from_user.id)]}
        response = requests.patch(API_URL + 'media_content/' + requested_id + '/', data=json.dumps(obj_data),
                                  headers=headers)
    markup = get_media_content_keyboard()
    bot.edit_message_reply_markup(chat_id, call.message.id, reply_markup=markup)


def get_current_user(message):
    try:
        user_id = message.from_user.id
        received_response = requests.get(API_URL + 'users/' + str(user_id))
        received_data = json.loads(received_response.content)
        if 'status_code' in received_data and received_data['status_code'] != 200:
            raise CustomUnauthenticated()
        return received_data
    except CustomUnauthenticated as e:
        handle_unauthenticated(message)
        return None


def handle_unauthenticated(message):
    chat_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/authenticate')
    bot.send_message(chat_id,
                     'Приветствую, жалкий кожаный мешок! Я лучший в мире, а ты ... ноунейм. Отправь '
                     '/authenticate чтобы зарегаться в системе', reply_markup=keyboard)


@bot.message_handler(commands=['authenticate'])
def authenticate_command(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    received_response = requests.get(API_URL + 'users/' + str(user_id))
    received_data = json.loads(received_response.content)
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/start')
    if 'status_code' in received_data and received_data['status_code'] != 200:
        requests.post(API_URL + 'users/', data={'external_id': str(message.from_user.id),
                                                'name': message.from_user.first_name})
        bot.send_message(chat_id, 'Ты зареган, можешь начинать растворяться в творчестве Величайшего',
                         reply_markup=keyboard)
    else:
        bot.send_message(chat_id, 'Ты уже зареган! Ты интеллект вообще качать собираешься?',
                         reply_markup=keyboard)


def get_media_content_keyboard():
    content_data = json.loads(requests.get(API_URL + 'media_content/').content)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    for content in content_data:
        content_button = telebot.types.InlineKeyboardButton(text=content['displayed_name'],
                                                            callback_data=f"/media_content_show_{content['id']}")

        like_button = telebot.types.InlineKeyboardButton(text=f"{content['likes']} лайков",
                                                         callback_data=f"/media_content_like_{content['id']}")
        markup.add(content_button, like_button)
    return markup


def get_default_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/media_content_index', '/media_content_new', '/help')
    return keyboard


class CustomUnauthenticated(Exception):
    pass


@bot.message_handler(content_types=['text'])
def handle_unsupported_command(message):
    bot.send_message(message.chat.id, 'Что ты там бубнишь? Используй нормальные команды, которые есть в "/help".')


if __name__ == '__main__':
    server.run()
