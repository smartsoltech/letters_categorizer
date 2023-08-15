import telebot
import os
from main import LetterCategorizer, param  # Импортируем основной класс для категоризации писем
from dotenv import load_dotenv

load_dotenv('.env')

# Настройки
TOKEN = os.getenv('TG_TOKEN')
bot = telebot.TeleBot(TOKEN)

categorizer = LetterCategorizer(input_path='input.csv', output_path='output.csv')

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

    # Обработка файла и сохранение результата
    output_path = "categorized_file.csv"
    categorizer = LetterCategorizer(src, output_path)
    categorizer.run()

    bot.send_document(chat_id=chat_id, document=open(output_path, 'rb'))

    # Удаляем оба файла
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
