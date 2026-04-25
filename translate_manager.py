import json
import os
from typing import Dict

class TranslationManager:
    def __init__(self):
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        for language in ['en', 'ukr', "ru"]:
            path = f'Locales/{language}.json'
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self.translations[language] = json.load(f)

    def get(self, key, language='en') -> str | Dict[str, str]:
        lang_dict = self.translations.get(language)
        return lang_dict.get(key, key)

translate_manager = TranslationManager()