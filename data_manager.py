import os
import json
import time
from datetime import datetime

class DataManager:
    """
    Класс для управления данными приложения.
    В реальном проекте здесь должна быть работа с базой данных,
    но для демонстрации используем файловую систему.
    """
    
    def __init__(self, data_dir='data'):
        """Инициализация менеджера данных."""
        self.data_dir = data_dir
        
        # Создаем директорию для данных, если она не существует
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        # Пути к файлам с данными
        self.business_types_file = os.path.join(data_dir, 'business_types.json')
        self.features_file = os.path.join(data_dir, 'features.json')
        self.examples_file = os.path.join(data_dir, 'examples.json')
        self.articles_file = os.path.join(data_dir, 'articles.json')
        self.messages_file = os.path.join(data_dir, 'messages.json')
        
        # Инициализируем файлы, если они не существуют
        self._init_data_files()
    
    def _init_data_files(self):
        """Инициализирует файлы с данными, если они не существуют."""
        files_default = {
            self.business_types_file: [],
            self.features_file: [],
            self.examples_file: [],
            self.articles_file: [],
            self.messages_file: []
        }
        
        for file_path, default_value in files_default.items():
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_value, f, ensure_ascii=False, indent=2)
    
    def _load_data(self, file_path):
        """Загружает данные из файла."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_data(self, file_path, data):
        """Сохраняет данные в файл."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self, existing_items):
        """Генерирует уникальный идентификатор для нового элемента."""
        if not existing_items:
            return "1"
        
        max_id = max(int(item.get('id', 0)) for item in existing_items)
        return str(max_id + 1)
    
    def _get_timestamp(self):
        """Возвращает текущую дату и время в формате строки."""
        return datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    
    # Методы для работы с типами бизнеса
    
    def get_business_types(self):
        """Возвращает список всех типов бизнеса."""
        return self._load_data(self.business_types_file)
    
    def get_business_type(self, type_id):
        """Возвращает тип бизнеса по ID."""
        business_types = self.get_business_types()
        for business_type in business_types:
            if business_type.get('id') == type_id:
                return business_type
        return None
    
    def add_business_type(self, name, base_price, description=''):
        """Добавляет новый тип бизнеса."""
        business_types = self.get_business_types()
        
        new_type = {
            'id': self._generate_id(business_types),
            'name': name,
            'base_price': base_price,
            'description': description,
            'created_at': self._get_timestamp(),
            'updated_at': self._get_timestamp()
        }
        
        business_types.append(new_type)
        self._save_data(self.business_types_file, business_types)
        return new_type
    
    def update_business_type(self, type_id, name, base_price, description=''):
        """Обновляет существующий тип бизнеса."""
        business_types = self.get_business_types()
        
        for i, business_type in enumerate(business_types):
            if business_type.get('id') == type_id:
                business_types[i].update({
                    'name': name,
                    'base_price': base_price,
                    'description': description,
                    'updated_at': self._get_timestamp()
                })
                self._save_data(self.business_types_file, business_types)
                return business_types[i]
        
        return None
    
    def delete_business_type(self, type_id):
        """Удаляет тип бизнеса."""
        business_types = self.get_business_types()
        
        for i, business_type in enumerate(business_types):
            if business_type.get('id') == type_id:
                removed = business_types.pop(i)
                self._save_data(self.business_types_file, business_types)
                return removed
        
        return None
    
    # Методы для работы с дополнительными услугами (функциями)
    
    def get_features(self):
        """Возвращает список всех дополнительных услуг."""
        return self._load_data(self.features_file)
    
    def get_feature(self, feature_id):
        """Возвращает дополнительную услугу по ID."""
        features = self.get_features()
        for feature in features:
            if feature.get('id') == feature_id:
                return feature
        return None
    
    def add_feature(self, name, price, description=''):
        """Добавляет новую дополнительную услугу."""
        features = self.get_features()
        
        new_feature = {
            'id': self._generate_id(features),
            'name': name,
            'price': price,
            'description': description,
            'created_at': self._get_timestamp(),
            'updated_at': self._get_timestamp()
        }
        
        features.append(new_feature)
        self._save_data(self.features_file, features)
        return new_feature
    
    def update_feature(self, feature_id, name, price, description=''):
        """Обновляет существующую дополнительную услугу."""
        features = self.get_features()
        
        for i, feature in enumerate(features):
            if feature.get('id') == feature_id:
                features[i].update({
                    'name': name,
                    'price': price,
                    'description': description,
                    'updated_at': self._get_timestamp()
                })
                self._save_data(self.features_file, features)
                return features[i]
        
        return None
    
    def delete_feature(self, feature_id):
        """Удаляет дополнительную услугу."""
        features = self.get_features()
        
        for i, feature in enumerate(features):
            if feature.get('id') == feature_id:
                removed = features.pop(i)
                self._save_data(self.features_file, features)
                return removed
        
        return None
    
    # Методы для работы с примерами успешных бизнес-проектов
    
    def get_examples(self):
        """Возвращает список всех примеров бизнес-проектов."""
        return self._load_data(self.examples_file)
    
    def get_example(self, example_id):
        """Возвращает пример бизнес-проекта по ID."""
        examples = self.get_examples()
        for example in examples:
            if example.get('id') == example_id:
                return example
        return None
    
    def add_example(self, title, business_type, investment, profit, period, content, image=''):
        """Добавляет новый пример бизнес-проекта."""
        examples = self.get_examples()
        
        new_example = {
            'id': self._generate_id(examples),
            'title': title,
            'business_type': business_type,
            'investment': investment,
            'profit': profit,
            'period': period,
            'content': content,
            'image': image,
            'created_at': self._get_timestamp(),
            'updated_at': self._get_timestamp()
        }
        
        examples.append(new_example)
        self._save_data(self.examples_file, examples)
        return new_example
    
    def update_example(self, example_id, title, business_type, investment, profit, period, content, image=''):
        """Обновляет существующий пример бизнес-проекта."""
        examples = self.get_examples()
        
        for i, example in enumerate(examples):
            if example.get('id') == example_id:
                examples[i].update({
                    'title': title,
                    'business_type': business_type,
                    'investment': investment,
                    'profit': profit,
                    'period': period,
                    'content': content,
                    'image': image,
                    'updated_at': self._get_timestamp()
                })
                self._save_data(self.examples_file, examples)
                return examples[i]
        
        return None
    
    def delete_example(self, example_id):
        """Удаляет пример бизнес-проекта."""
        examples = self.get_examples()
        
        for i, example in enumerate(examples):
            if example.get('id') == example_id:
                removed = examples.pop(i)
                self._save_data(self.examples_file, examples)
                return removed
        
        return None
    
    # Методы для работы со статьями базы знаний
    
    def get_articles(self):
        """Возвращает список всех статей."""
        return self._load_data(self.articles_file)
    
    def get_article(self, article_id):
        """Возвращает статью по ID."""
        articles = self.get_articles()
        for article in articles:
            if article.get('id') == article_id:
                return article
        return None
    
    def add_article(self, title, category, description, content, image=''):
        """Добавляет новую статью."""
        articles = self.get_articles()
        
        # Форматируем дату публикации
        date = datetime.now().strftime('%d %B %Y')
        
        new_article = {
            'id': self._generate_id(articles),
            'title': title,
            'category': category,
            'description': description,
            'content': content,
            'image': image,
            'date': date,
            'created_at': self._get_timestamp(),
            'updated_at': self._get_timestamp()
        }
        
        articles.append(new_article)
        self._save_data(self.articles_file, articles)
        return new_article
    
    def update_article(self, article_id, title, category, description, content, image=''):
        """Обновляет существующую статью."""
        articles = self.get_articles()
        
        for i, article in enumerate(articles):
            if article.get('id') == article_id:
                # Сохраняем оригинальную дату публикации
                original_date = article.get('date')
                
                articles[i].update({
                    'title': title,
                    'category': category,
                    'description': description,
                    'content': content,
                    'image': image,
                    'date': original_date,  # Оставляем оригинальную дату
                    'updated_at': self._get_timestamp()
                })
                self._save_data(self.articles_file, articles)
                return articles[i]
        
        return None
    
    def delete_article(self, article_id):
        """Удаляет статью."""
        articles = self.get_articles()
        
        for i, article in enumerate(articles):
            if article.get('id') == article_id:
                removed = articles.pop(i)
                self._save_data(self.articles_file, articles)
                return removed
        
        return None
    
    # Методы для работы с сообщениями пользователей
    
    def get_messages(self):
        """Возвращает список всех сообщений."""
        return self._load_data(self.messages_file)
    
    def get_message(self, message_id):
        """Возвращает сообщение по ID."""
        messages = self.get_messages()
        for message in messages:
            if message.get('id') == message_id:
                return message
        return None
    
    def add_message(self, name, email, subject, content):
        """Добавляет новое сообщение."""
        messages = self.get_messages()
        
        new_message = {
            'id': self._generate_id(messages),
            'name': name,
            'email': email,
            'subject': subject,
            'content': content,
            'is_read': False,
            'created_at': self._get_timestamp(),
            'updated_at': self._get_timestamp()
        }
        
        messages.append(new_message)
        self._save_data(self.messages_file, messages)
        return new_message
    
    def mark_message_as_read(self, message_id):
        """Отмечает сообщение как прочитанное."""
        messages = self.get_messages()
        
        for i, message in enumerate(messages):
            if message.get('id') == message_id:
                messages[i]['is_read'] = True
                messages[i]['updated_at'] = self._get_timestamp()
                self._save_data(self.messages_file, messages)
                return messages[i]
        
        return None
    
    def delete_message(self, message_id):
        """Удаляет сообщение."""
        messages = self.get_messages()
        
        for i, message in enumerate(messages):
            if message.get('id') == message_id:
                removed = messages.pop(i)
                self._save_data(self.messages_file, messages)
                return removed
        
        return None 