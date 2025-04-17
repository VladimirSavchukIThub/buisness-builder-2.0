import psycopg2
from datetime import datetime
from config import business_options

# Подключение к базе данных
conn = psycopg2.connect(
    user="postgres",
    password="postgres",
    host="localhost",
    port="5433",
    database="business_constructor"
)

# Устанавливаем автоматическое подтверждение транзакций
conn.autocommit = True
cursor = conn.cursor()

# Заполнение таблицы business_types
print("Заполнение таблицы business_types...")
for business_type in business_options['business_types']:
    # Проверка, существует ли уже такая запись
    cursor.execute("SELECT COUNT(*) FROM business_types WHERE name = %s", (business_type['name'],))
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO business_types (name, base_price, description, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
            (
                business_type['name'],
                business_type['base_price'],
                "",  # Пустое описание
                datetime.now(),
                datetime.now()
            )
        )
        print(f"  Добавлен тип бизнеса: {business_type['name']}")
    else:
        print(f"  Тип бизнеса {business_type['name']} уже существует")

# Заполнение таблицы business_sizes
print("\nЗаполнение таблицы business_sizes...")
for business_size in business_options['business_sizes']:
    # Проверка, существует ли уже такая запись
    cursor.execute("SELECT COUNT(*) FROM business_sizes WHERE name = %s", (business_size['name'],))
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO business_sizes (name, multiplier, description, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
            (
                business_size['name'],
                business_size['multiplier'],
                "",  # Пустое описание
                datetime.now(),
                datetime.now()
            )
        )
        print(f"  Добавлен размер бизнеса: {business_size['name']}")
    else:
        print(f"  Размер бизнеса {business_size['name']} уже существует")

# Заполнение таблицы features
print("\nЗаполнение таблицы features...")
for feature in business_options['features']:
    # Проверка, существует ли уже такая запись
    cursor.execute("SELECT COUNT(*) FROM features WHERE name = %s", (feature['name'],))
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO features (name, price, description, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
            (
                feature['name'],
                feature['price'],
                "",  # Пустое описание
                datetime.now(),
                datetime.now()
            )
        )
        print(f"  Добавлена функция: {feature['name']}")
    else:
        print(f"  Функция {feature['name']} уже существует")

# Добавим примеры успешных бизнес-проектов, если их нет
print("\nЗаполнение таблицы examples...")
examples = [
    {
        'title': 'Кофейня "Утренний аромат"',
        'business_type': 'Сфера услуг',
        'investment': 1500000,
        'profit': 250000,
        'period': '6 месяцев',
        'content': 'Кофейня в центре города с уникальным ассортиментом напитков и десертов. Благодаря удачному расположению и качественному сервису бизнес быстро вышел на окупаемость.'
    },
    {
        'title': 'Интернет-магазин "ТехноМир"',
        'business_type': 'Онлайн-бизнес',
        'investment': 800000,
        'profit': 180000,
        'period': '4 месяца',
        'content': 'Магазин электроники с продуманной логистикой и маркетинговой стратегией. Благодаря оптимизации расходов и эффективному продвижению в социальных сетях достигнута высокая рентабельность.'
    },
    {
        'title': 'Пекарня "Свежий хлеб"',
        'business_type': 'Производство',
        'investment': 2200000,
        'profit': 300000,
        'period': '8 месяцев',
        'content': 'Пекарня полного цикла с собственным производством и розничной точкой. Использование натуральных ингредиентов и старинных рецептов позволило создать востребованный продукт.'
    }
]

for example in examples:
    # Проверка, существует ли уже такая запись
    cursor.execute("SELECT COUNT(*) FROM examples WHERE title = %s", (example['title'],))
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO examples (title, business_type, investment, profit, period, content, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                example['title'],
                example['business_type'],
                example['investment'],
                example['profit'],
                example['period'],
                example['content'],
                datetime.now(),
                datetime.now()
            )
        )
        print(f"  Добавлен пример: {example['title']}")
    else:
        print(f"  Пример {example['title']} уже существует")

# Добавим статьи для базы знаний, если их нет
print("\nЗаполнение таблицы articles...")
articles = [
    {
        'title': 'Как составить эффективный бизнес-план',
        'category': 'Планирование',
        'description': 'Практическое руководство по созданию бизнес-плана, который привлечет инвесторов',
        'content': 'Бизнес-план – это документ, описывающий все основные аспекты будущего предприятия. Он анализирует проблемы, с которыми оно может столкнуться, а также определяет способы решения этих проблем. Грамотно составленный бизнес-план является основой успеха любого бизнеса и ключевым инструментом для привлечения инвестиций.\n\nОсновные разделы бизнес-плана:\n1. Резюме проекта\n2. Описание компании и продукта/услуги\n3. Анализ рынка и конкурентов\n4. Маркетинговая стратегия\n5. Производственный план\n6. Организационный план\n7. Финансовый план\n8. Анализ рисков\n\nКаждый из этих разделов требует тщательной проработки и подкрепления реальными цифрами. Помните, что инвесторы ищут конкретику, а не общие фразы.',
        'featured': True
    },
    {
        'title': 'Оптимизация налогообложения для малого бизнеса',
        'category': 'Финансы',
        'description': 'Законные способы снижения налоговой нагрузки для предпринимателей',
        'content': 'Налоговая оптимизация – это комплекс мер, направленных на законное уменьшение налоговых платежей. Для малого бизнеса доступны различные специальные налоговые режимы, которые позволяют снизить налоговую нагрузку и упростить учет.\n\nОсновные специальные налоговые режимы:\n1. Упрощенная система налогообложения (УСН)\n2. Патентная система налогообложения (ПСН)\n3. Налог на профессиональный доход (для самозанятых)\n\nПравильный выбор налогового режима зависит от множества факторов: вида деятельности, ожидаемого оборота, количества сотрудников и т.д. Регулярный анализ налоговой нагрузки и своевременная корректировка бизнес-процессов позволят сэкономить значительные средства.',
        'featured': False
    },
    {
        'title': 'Эффективные стратегии привлечения клиентов',
        'category': 'Маркетинг',
        'description': 'Современные методы привлечения и удержания клиентов для различных типов бизнеса',
        'content': 'В современном конкурентном мире привлечение новых клиентов требует комплексного подхода и использования различных каналов коммуникации. Успешная стратегия должна основываться на глубоком понимании целевой аудитории и ее потребностей.\n\nНаиболее эффективные методы привлечения клиентов:\n1. Контент-маркетинг – создание ценного контента, который решает проблемы потенциальных клиентов\n2. SMM – продвижение в социальных сетях с использованием таргетированной рекламы\n3. SEO – оптимизация сайта для поисковых систем\n4. Email-маркетинг – построение долгосрочных отношений с помощью рассылок\n5. Партнерские программы – привлечение клиентов через партнеров\n\nНе менее важно уделять внимание удержанию существующих клиентов, ведь привлечение нового клиента стоит в 5-7 раз дороже, чем удержание существующего. Программы лояльности, персонализированные предложения и высокий уровень сервиса помогут сформировать базу постоянных клиентов.',
        'featured': True
    }
]

for article in articles:
    # Проверка, существует ли уже такая запись
    cursor.execute("SELECT COUNT(*) FROM articles WHERE title = %s", (article['title'],))
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO articles (title, category, description, content, featured, date, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                article['title'],
                article['category'],
                article['description'],
                article['content'],
                article['featured'],
                datetime.now().strftime('%d %B %Y'),
                datetime.now(),
                datetime.now()
            )
        )
        print(f"  Добавлена статья: {article['title']}")
    else:
        print(f"  Статья {article['title']} уже существует")

# Закрытие соединения
cursor.close()
conn.close()

print("\nЗаполнение базы данных успешно завершено!") 