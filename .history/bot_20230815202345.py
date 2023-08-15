import telebot
import os
from main import LetterCategorizer, param  # Импортируем основной класс для категоризации писем

# Настройки
TOKEN = param['settings']['tg_bot_token'][0]
bot = telebot.TeleBot(TOKEN)

categorizer = LetterCategorizer(input_path='input.csv', output_path='output.csv')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне CSV-файл с письмами, и я категоризирую их для тебя.")

@bot.message_handler(func=lambda message: True, content_types=['document'])
def categorize_file(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("input.csv", 'wb') as new_file:
            new_file.write(downloaded_file)

        categorizer.run()

        with open("output.csv", 'rb') as output:
            bot.send_document(message.chat.id, output)

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

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
