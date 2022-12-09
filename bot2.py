import os
import telebot
import requests
import speech_recognition as sr
import subprocess
import datetime

import random


from telebot import types
logfile = str(datetime.date.today()) + '.log'
token = 'XXXXXXX'
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def welcome(message):
  sti = open('welcome.webp', 'rb')
  bot.send_sticker(message.chat.id , sti)

  # keyboard  (обычная)
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  item1 = types.KeyboardButton("🎲 Рандомное число")
  item2 = types.KeyboardButton("😊 Как дела?")

  markup.add(item1, item2)#Добавляем объект марка при помощи метода add

  bot.send_message(message.chat.id, "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот созданный быть подопытным кроликом.".format(message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)
  # Прикрепил клавиатуру к боту (reply_markup=markup)


@bot.message_handler(content_types=['text'])
def lalala(message):
    if message.chat.type == 'private':
        if message.text == '🎲 Рандомное число':
          bot.send_message(message.chat.id , str(random.randint(0,100)))
        elif message.text == '😊 Как дела?':
          #Инлайновая клавиатура
          markup = types.InlineKeyboardMarkup(row_width=2)
          item1 = types.InlineKeyboardButton("Хорошо", callback_data='good')
          item2 = types.InlineKeyboardButton("Не очень", callback_data='bad')
          
          markup.add(item1, item2) #Прикрепил инлайновую клавиатуру методом add 

          bot.send_message(message.chat.id, 'Отлично, сам как?', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Я не знаю что ответить 😢')


#Обработка нажатия инлайновой клавиатуры
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'good':
                bot.send_message(call.message.chat.id, 'Вот и отличненько 😊')
            elif call.data == 'bad':
                bot.send_message(call.message.chat.id, 'Бывает 😢')

            # remove inline buttons
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="😊 Как дела?", reply_markup=None)

            # show alert
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="ЭТО ТЕСТОВОЕ УВЕДОМЛЕНИЕ!!")

    except Exception as e:
        print(repr(e))





#Работа с аудио
def audio_to_text(dest_name: str):
# Функция для перевода аудио , в формате ".vaw" в текст
    r = sr.Recognizer() # такое вообще надо комментить?
    # тут мы читаем наш .vaw файл
    message = sr.AudioFile(dest_name)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU") # здесь можно изменять язык распознавания
    return result


@bot.message_handler(content_types=['voice'])
def get_audio_messages(message):
# Основная функция, принимает голосовуху от пользователя
    try:
        print("Started recognition...")
        # Ниже пытаемся вычленить имя файла, да и вообще берем данные с мессаги
        file_info = bot.get_file(message.voice.file_id)
        path = file_info.file_path # Вот тут-то и полный путь до файла (например: voice/file_2.oga)
        fname = os.path.basename(path) # Преобразуем путь в имя файла (например: file_2.oga)
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))# Получаем и сохраняем присланную голосвуху (Ага, админ может в любой момент отключить удаление айдио файлов и слушать все, что ты там говоришь. А представь, что такую бяку подселят в огромный чат и она будет просто логировать все сообщения [анонимность в телеграмме, ахахаха])
        with open(fname+'.oga', 'wb') as f:
            f.write(doc.content) # вот именно тут и сохраняется сама аудио-мессага
        process = subprocess.run(['ffmpeg', '-i', fname+'.oga', fname+'.wav'])# здесь используется страшное ПО ffmpeg, для конвертации .oga в .vaw
        result = audio_to_text(fname+'.wav') # Вызов функции для перевода аудио в текст, а заодно передаем имена файлов, для их последующего удаления
        bot.send_message(message.from_user.id, format(result))
    except sr.UnknownValueError as e:
        bot.send_message(message.from_user.id,  "Прошу прощения, но я не разобрал сообщение, или оно поустое...")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(message.from_user.username) +':'+ str(message.from_user.language_code) + ':Message is empty.\n')
    except Exception as e:
        bot.send_message(message.from_user.id,  "Что-то пошло не так, как задумано")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(message.from_user.username) +':'+ str(message.from_user.language_code) +':' + str(e) + '\n')
    finally:
        os.remove(fname+'.wav')
        os.remove(fname+'.oga')

bot.polling(none_stop=True, interval=0)# Очень не культурно стучимся телеге и проверяем наличие сообщений