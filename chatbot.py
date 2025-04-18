import re
from difflib import get_close_matches
import random

class ChatBot:
    def __init__(self):
        # База знаний: вопросы и ответы
        self.qa_database = {
            'бизнес_план': [
                "Как составить бизнес-план?",
                "Что включить в бизнес-план?",
                "Структура бизнес-плана",
                "Пример бизнес-плана"
            ],
            'налоги': [
                "Какие налоги платит ИП?",
                "Налоги для ООО",
                "Налоговые льготы для малого бизнеса",
                "Выбор системы налогообложения"
            ],
            'регистрация': [
                "Как открыть ИП?",
                "Регистрация ООО",
                "Документы для регистрации бизнеса",
                "Сроки регистрации бизнеса"
            ],
            'финансирование': [
                "Где взять деньги на бизнес?",
                "Кредит для бизнеса",
                "Инвесторы для стартапа",
                "Государственная поддержка бизнеса"
            ],
            'маркетинг': [
                "Как продвигать бизнес?",
                "Маркетинг для малого бизнеса",
                "Реклама с минимальным бюджетом",
                "Социальные сети для бизнеса"
            ]
        }
        
        # Ответы по категориям
        self.answers = {
            'бизнес_план': [
                "Хороший бизнес-план должен включать: резюме проекта, описание компании, анализ рынка, "
                "маркетинговый план, операционный план и финансовые прогнозы. В нашей базе знаний есть подробная "
                "статья на эту тему. Хотите, я дам вам ссылку?",
                
                "Для составления бизнес-плана рекомендую использовать структуру из 7 разделов: резюме, описание "
                "бизнеса, анализ рынка, стратегия и реализация, организационный план, финансовый план и приложения. "
                "В разделе 'База знаний' вы найдете детальное руководство."
            ],
            'налоги': [
                "ИП может выбрать одну из систем налогообложения: ОСНО, УСН (6% от доходов или 15% от доходов минус "
                "расходы), НПД (для самозанятых), ПСН. Выбор зависит от вида деятельности, оборота и других факторов. "
                "В нашей базе знаний есть статья по оптимизации налогообложения.",
                
                "Для ООО доступны следующие системы налогообложения: ОСНО (20% налог на прибыль, НДС 20%, налог на "
                "имущество), УСН (6% от доходов или 15% от доходов минус расходы). Оптимальный выбор зависит от "
                "специфики бизнеса."
            ],
            'регистрация': [
                "Чтобы открыть ИП, нужно подготовить паспорт, заявление по форме Р21001, квитанцию об уплате "
                "госпошлины (если подаете документы не через госуслуги). Подать документы можно через МФЦ, "
                "налоговую или портал Госуслуги. Срок регистрации - 3 рабочих дня.",
                
                "Для регистрации ООО необходимы: заявление по форме Р11001, устав компании, решение о создании, "
                "квитанция об уплате госпошлины, документ об адресе компании. Подать можно в МФЦ, налоговую или "
                "через Госуслуги."
            ],
            'финансирование': [
                "Основные источники финансирования для бизнеса включают: личные сбережения, кредиты и займы, "
                "инвестиции от бизнес-ангелов или венчурных фондов, краудфандинг, государственные гранты и "
                "субсидии. В разделе 'База знаний' есть статья о программах поддержки предпринимателей.",
                
                "Для получения бизнес-кредита подготовьте бизнес-план, финансовую отчетность и обеспечение. "
                "Средняя ставка для малого бизнеса сейчас составляет 15-18% годовых. Также можно рассмотреть "
                "льготные программы кредитования от государства со ставкой от 7-10%."
            ],
            'маркетинг': [
                "Для продвижения малого бизнеса с минимальным бюджетом рекомендую: создание профилей в социальных "
                "сетях, email-маркетинг, контент-маркетинг, сотрудничество с другими бизнесами, участие в местных "
                "мероприятиях и использование сарафанного радио. В нашей базе знаний есть подробная статья по "
                "маркетинговым стратегиям.",
                
                "Социальные сети - мощный инструмент для продвижения бизнеса. Выберите 1-2 платформы, где "
                "присутствует ваша целевая аудитория, создавайте регулярный контент, взаимодействуйте с "
                "аудиторией и используйте таргетированную рекламу."
            ],
            'default': [
                "Извините, я не совсем понял ваш вопрос. Попробуйте сформулировать его иначе или выберите одну из "
                "популярных тем: составление бизнес-плана, налогообложение, регистрация бизнеса, финансирование или "
                "маркетинг.",
                
                "Кажется, у меня нет точной информации по вашему вопросу. Могу предложить изучить раздел 'База знаний' "
                "на нашем сайте или задать более конкретный вопрос о бизнес-планировании, налогах, регистрации или "
                "финансировании бизнеса."
            ]
        }
        
        # Ключевые слова для определения темы вопроса
        self.keywords = {
            'бизнес_план': ['бизнес-план', 'бизнес план', 'план бизнеса', 'планирование', 'стратегия', 'прогноз'],
            'налоги': ['налог', 'налоги', 'налогообложение', 'ндс', 'усн', 'осно', 'патент', 'налоговый'],
            'регистрация': ['регистрация', 'открыть', 'создать', 'оформить', 'ип', 'ооо', 'юрлицо', 'документы'],
            'финансирование': ['деньги', 'кредит', 'заем', 'инвестиции', 'финансирование', 'субсидия', 'грант', 'займ'],
            'маркетинг': ['маркетинг', 'реклама', 'продвижение', 'клиенты', 'продажи', 'сайт', 'соцсети', 'продвигать']
        }
        
        # Приветственные фразы
        self.greetings = [
            "Здравствуйте! Я виртуальный консультант по бизнесу. Чем могу помочь?",
            "Добрый день! Я здесь, чтобы ответить на ваши вопросы о бизнесе. Что вас интересует?",
            "Приветствую! Я - чат-бот консультант по бизнесу. Задайте вопрос, и я постараюсь помочь.",
            "Здравствуйте! Я помогу вам с информацией о бизнесе. Какой у вас вопрос?"
        ]
        
        # Прощальные фразы
        self.goodbyes = [
            "Всего доброго! Если возникнут еще вопросы, обращайтесь.",
            "До свидания! Рад был помочь. Заходите еще.",
            "Удачи в вашем бизнесе! Обращайтесь, если понадобится дополнительная информация.",
            "Всего хорошего! Надеюсь, информация была полезной."
        ]
    
    def get_greeting(self):
        """Возвращает случайное приветствие"""
        return random.choice(self.greetings)
    
    def get_goodbye(self):
        """Возвращает случайную прощальную фразу"""
        return random.choice(self.goodbyes)
    
    def classify_query(self, query):
        """Определяет категорию запроса пользователя"""
        query = query.lower()
        
        # Проверяем на прощание
        goodbye_keywords = ['пока', 'до свидания', 'прощай', 'до встречи', 'удачи', 'хватит']
        if any(word in query for word in goodbye_keywords):
            return 'goodbye'
        
        # Поиск по ключевым словам
        max_matches = 0
        best_category = 'default'
        
        for category, keywords in self.keywords.items():
            matches = sum(1 for word in keywords if word in query)
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        # Если не нашли ключевых слов, пробуем найти похожие вопросы
        if max_matches == 0:
            for category, questions in self.qa_database.items():
                # Создаем список всех слов из вопросов в категории
                all_words = []
                for question in questions:
                    all_words.extend(question.lower().split())
                
                # Проверяем, сколько слов из запроса пользователя есть в списке
                query_words = query.split()
                matches = sum(1 for word in query_words if word in all_words)
                
                if matches > max_matches:
                    max_matches = matches
                    best_category = category
        
        return best_category
    
    def get_response(self, query):
        """Возвращает ответ на запрос пользователя"""
        # Определяем категорию запроса
        category = self.classify_query(query)
        
        # Если это прощание, возвращаем прощальную фразу
        if category == 'goodbye':
            return self.get_goodbye()
        
        # Выбираем случайный ответ из категории
        if category in self.answers:
            return random.choice(self.answers[category])
        
        # Если категория не определена, возвращаем ответ по умолчанию
        return random.choice(self.answers['default'])

# Пример использования
if __name__ == "__main__":
    bot = ChatBot()
    print(bot.get_greeting())
    
    while True:
        query = input("> ")
        if query.lower() in ['выход', 'exit', 'quit']:
            print(bot.get_goodbye())
            break
        
        response = bot.get_response(query)
        print(response) 