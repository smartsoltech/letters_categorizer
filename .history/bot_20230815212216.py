import telebot
import os
import pandas as pd
from main import LetterCategorizer, LetterProcessor, param
from dotenv import load_dotenv

load_dotenv('.env')

# Настройки
bot = telebot.TeleBot(os.getenv('TG_BOT'))

GPT_TOKEN = os.getenv('GPT_TOKEN')
categorizer = LetterCategorizer(input_path='input.csv', output_path='output.csv')

def send_long_message(chat_id, message_text):
    max_message_length = 4096  # Maximum length of a message
    for i in range(0, len(message_text), max_message_length):
        chunk = message_text[i:i + max_message_length]
        bot.send_message(chat_id, chunk)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне CSV-файл с письмами, и я категоризирую их для тебя.")

@bot.message_handler(content_types=['document'])
def categorize_file(message):
    chat_id = message.chat.id
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    src = 'received_file.csv'
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.send_message(chat_id, "Начинаю обработку файла...")

    # Подготовка данных и запуск процесса
    initial_keywords = sum(param['keywords'].values(), [])
    data = pd.read_csv(src, encoding='UTF-8')

    # Расширение словаря ключевых слов
    processor = LetterProcessor(GPT_TOKEN, initial_keywords)
    processor.extend_dictionary_with_letters(data)

    # Получение расширенного словаря и новых ключевых слов
    new_dictionary = processor.get_extended_dictionary()
    new_keywords = set(new_dictionary) - set(initial_keywords)

    # Категоризация писем
    output_path = "categorized_file.csv"
    categorizer = LetterCategorizer(src, output_path)
    categorizer.run()

    # Отправка результатов
    bot.send_document(chat_id=chat_id, document=open(output_path, 'rb'))
    if new_keywords:
        new_keywords_str = '\n'.join(new_keywords)
        bot.send_message(chat_id, f"Новые ключевые слова, добавленные в словарь:\n\n{new_keywords_str}")

    bot.send_message(chat_id, "Обработка файла завершена.")

    # Удаление файлов
    remove_file(src)
    remove_file(output_path)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Пожалуйста, отправь мне CSV-файл.")

def remove_file(filepath):
    """Удаляет файл по указанному пути, если он существует."""
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        print(f"Файл {filepath} не найден.")

if __name__ == "__main__":
    bot.polling(none_stop=True)
