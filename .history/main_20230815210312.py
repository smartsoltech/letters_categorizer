import pandas as pd
import yaml
import os
from dotenv import load_dotenv
import openai as ai

# Загрузка переменных окружения
load_dotenv()

# Получение токенов из переменных окружения
GPT_TOKEN = os.getenv('GPT_TOKEN')
TG_BOT = os.getenv('TG_BOT')

# Загрузка настроек из файла settings.yaml
with open('settings.yaml', 'r', encoding='UTF-8') as tmp_data:
    param = yaml.safe_load(tmp_data)


class LetterProcessor:
    def __init__(self, openai_api_key, initial_keywords):
        self.api_key = openai_api_key
        self.keywords = set(initial_keywords)
        ai.api_key = self.api_key

    def extract_keywords_from_gpt_response(self, response):
        return set(response.split())

    def extend_dictionary_with_letters(self, dataframe):
        letters = dataframe[dataframe.columns[0]].tolist()
        for letter in letters:
            prompt = f"Extract keywords from the following text: {letter}"
            response = ai.Completion.create(engine="davinci", prompt=prompt, max_tokens=50)
            new_keywords = self.extract_keywords_from_gpt_response(response.choices[0].text.strip())
            self.keywords.update(new_keywords)

    def get_extended_dictionary(self):
        return list(self.keywords)


class LetterCategorizer:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.data = None

        # Словарь с ключевыми словами для каждой категории
        self.keywords_dict = param['keywords']

    def load_data(self):
        try:
            self.data = pd.read_csv(self.input_path, encoding='windows-1251')
        except UnicodeDecodeError:
            self.data = pd.read_csv(self.input_path, encoding='utf-8-sig')

    def _categorize_letter(self, letter):
        categories = []
        for category, keywords in self.keywords_dict.items():
            for keyword in keywords:
                if keyword in letter.lower():
                    categories.append(category)
                    break
        return ', '.join(categories)

    def categorize_data(self):
        self.data['Categories'] = self.data[self.data.columns[0]].apply(self._categorize_letter)

    def save_results(self):
        grouped_data = self.data.groupby('Categories')[self.data.columns[0]].apply('\n'.join).reset_index()
        grouped_data.columns = ['Category', 'Mails']
        grouped_data.to_csv(self.output_path, index=False, encoding='utf-8-sig')

    def run(self):
        self.load_data()
        self.categorize_data()
        self.save_results()



