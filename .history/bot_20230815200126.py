import os
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from main import LetterCategorizer, param  # Импортируем основной класс для категоризации писем

# Настройки
TOKEN = param['settings']['tg_bot_token'][0]

def start(update: Update, context):
    update.message.reply_text("Привет! Отправь мне файл в формате CSV, и я категоризирую письма для тебя.")

def categorize_file(update: Update, context):
    file = update.message.document.get_file()
    file.download('input_file.csv')
    
    # Запускаем категоризатор
    categorizer = LetterCategorizer('input_file.csv', 'output_file.csv')
    categorizer.run()
    
    # Отправляем результат пользователю
    with open('output_file.csv', 'rb') as output:
        update.message.reply_document(output)

def main():
    updater = Updater(token=TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.document.mime_type("text/csv"), categorize_file))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
