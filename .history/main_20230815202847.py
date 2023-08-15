import pandas as pd
import yaml

with open('settings.yaml', 'r', encoding='UTF-8') as tmp_data:
    param = yaml.safe_load(tmp_data)

class LetterCategorizer:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.data = None
        
        
        # Словарь с ключевыми словами для каждой категории
        self.keywords_dict = param['keywords']
        
    def load_data_from_string(self, data_string):
        """Загрузка данных из строки."""
        from io import StringIO
        self.data = pd.read_csv(StringIO(data_string))
    def _categorize_letter(self, letter):
        """Категоризация письма на основе ключевых слов."""
        categories = []
        for category, keywords in self.keywords_dict.items():
            for keyword in keywords:
                if keyword in letter.lower():  # учет регистронезависимости
                    categories.append(category)
                    break  # переход к следующей категории после обнаружения ключевого слова
        return ', '.join(categories)

    def load_data(self):
        """Загрузка данных из CSV-файла."""
        self.data = pd.read_csv(self.input_path, encoding='windows-1251')
        
    def categorize_data(self):
        """Категоризация всех писем."""
        self.data['Categories'] = self.data[self.data.columns[0]].apply(self._categorize_letter)
        
    def save_results(self):
            """Сохранение результатов в CSV-файл."""
            # Группировка данных по категориям и объединение текстов писем
            grouped_data = self.data.groupby('Categories')[self.data.columns[0]].apply('\n'.join).reset_index()
            grouped_data.columns = ['Category', 'Mails']
            grouped_data.to_csv(self.output_path, index=False, encoding='windows-1251')
        
    def run(self):
        """Запуск процесса категоризации."""
        self.load_data()
        self.categorize_data()
        self.save_results()
