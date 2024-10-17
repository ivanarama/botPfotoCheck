import telebot
import pytesseract
import requests
from PIL import Image
from io import BytesIO
from openai import OpenAI
import os

TOKEN_file = f'auth.TOKEN'


with open(TOKEN_file, 'r') as file:
    TOKEN = file.read().replace('\n', '')
bot = telebot.TeleBot(TOKEN)
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
     if 'Иван' in message.text:
         bot.send_message(message.chat.id,"Ба! Знакомые все лица!")
     else:
         bot.send_message(message.chat.id,"Я тебя не знаю человег")
# Обработчик изображений
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Ответ пользователю при получении фото
    # Получаем ID файла
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    
    # Загружаем файл
    file_url = f'https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}'
    response = requests.get(file_url)

    # Открываем изображение с помощью PIL и конвертируем его для Tesseract
    img = Image.open(BytesIO(response.content))

    # Распознаем текст с изображения
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    image_to_string=pytesseract.image_to_string(img,lang= 'rus')
    

    # Отправляем распознанный текст пользователю
    bot.send_message(message.chat.id, f"Распознанный текст:\n{image_to_string}")
    api_key = os.environ.get("OPENAI_API_KEY")
    # Проверяем, что ключ был успешно получен
    if api_key is not None:
        print("API ключ получен успешно")
    else:
        print("Не удалось получить API ключ.")
    client = OpenAI(api_key=api_key)
    prompt = 'Найди опечатку в русском тексте :' + image_to_string
    messages = [{"role": "user", "content": prompt}]





    response = client.chat.completions.create(
    model="gpt-4o-2024-05-13",
    messages=messages,
    temperature=0.5,
    max_tokens=250,
    )
    answer = response.choices[0].message.content
    print(answer) 
    bot.send_message(message.chat.id, f"Обнаружены следующие опечатки:\n{answer}")

bot.polling(none_stop=True)