# Конфигурация для бизнес-конструктора

# Опции бизнеса
business_options = {
    'business_types': [
        {'id': 'retail', 'name': 'Розничная торговля', 'base_price': 500000},
        {'id': 'service', 'name': 'Сфера услуг', 'base_price': 300000},
        {'id': 'production', 'name': 'Производство', 'base_price': 1000000},
        {'id': 'online', 'name': 'Онлайн-бизнес', 'base_price': 200000}
    ],
    'business_sizes': [
        {'id': 'small', 'name': 'Малый', 'multiplier': 1.0},
        {'id': 'medium', 'name': 'Средний', 'multiplier': 2.0},
        {'id': 'large', 'name': 'Крупный', 'multiplier': 3.5}
    ],
    'features': [
        {'id': 'crm', 'name': 'CRM-система', 'price': 50000},
        {'id': 'analytics', 'name': 'Бизнес-аналитика', 'price': 80000},
        {'id': 'marketing', 'name': 'Маркетинговые услуги', 'price': 120000},
        {'id': 'logistics', 'name': 'Логистика', 'price': 150000},
        {'id': 'legal', 'name': 'Юридическое сопровождение', 'price': 100000},
        {'id': 'accounting', 'name': 'Бухгалтерский учет', 'price': 70000},
        {'id': 'hr', 'name': 'HR-сервисы', 'price': 60000},
        {'id': 'automation', 'name': 'Автоматизация процессов', 'price': 200000},
        {'id': 'training', 'name': 'Обучение персонала', 'price': 90000}
    ]
}

# Функция для расчета стоимости бизнеса
def calculate_price(data):
    # Получаем базовую цену для выбранного типа бизнеса
    business_type = data.get('business_type')
    base_price = next((t['base_price'] for t in business_options['business_types'] if t['id'] == business_type), 0)
    
    # Получаем множитель для выбранного размера бизнеса
    business_size = data.get('business_size')
    multiplier = next((s['multiplier'] for s in business_options['business_sizes'] if s['id'] == business_size), 1.0)
    
    # Рассчитываем стоимость с учетом размера
    price = base_price * multiplier
    
    # Добавляем стоимость выбранных функций
    features = data.get('features', [])
    for feature_id in features:
        feature_price = next((f['price'] for f in business_options['features'] if f['id'] == feature_id), 0)
        price += feature_price
    
    return int(price) 