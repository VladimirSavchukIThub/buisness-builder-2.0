from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file, make_response, abort
from config import business_options, calculate_price
import traceback
import os
import locale
from pdf_generator import generate_pdf
import urllib.parse
import json
from bank_api import get_business_loan_rates, calculate_business_loan, BankAPI

app = Flask(__name__)
app.secret_key = os.urandom(24)  # для работы с сессиями и flash-сообщениями

# Пытаемся установить русскую локаль для Windows
try:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
except locale.Error:
    try:
        # Альтернативное имя локали для Windows
        locale.setlocale(locale.LC_ALL, 'Russian_Russia.1251')
    except locale.Error:
        # Если не удалось, используем базовую локаль
        locale.setlocale(locale.LC_ALL, '')

# Добавляем фильтр для форматирования чисел
@app.template_filter('number_format')
def number_format_filter(value):
    try:
        # Форматирование числа с разделителями групп разрядов
        return locale.format_string("%d", int(value), grouping=True)
    except (ValueError, TypeError, locale.Error):
        # Если возникла ошибка, используем простое форматирование
        if isinstance(value, (int, float)):
            return f"{int(value):,}".replace(',', ' ')
        return value

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница конструктора бизнеса
@app.route('/constructor')
def constructor():
    return render_template('constructor.html', 
                           business_types=business_options['business_types'],
                           business_sizes=business_options['business_sizes'],
                           features=business_options['features'])

# Страница с информацией о проекте
@app.route('/about')
def about():
    return render_template('about.html')

# Страница с контактной информацией
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Страница с примерами успешных бизнес-моделей
@app.route('/examples')
def examples():
    return render_template('examples.html')

# Страница базы знаний
@app.route('/knowledge-base')
def knowledge_base():
    # Mock data for demonstration purposes
    articles = [
        {
            'id': 1,
            'title': 'Как составить бизнес-план для малого бизнеса',
            'description': 'Пошаговое руководство по созданию эффективного бизнес-плана для начинающих предпринимателей.',
            'category': 'Планирование',
            'image': url_for('static', filename='images/articles/business-plan.jpg'),
            'date': '15 мая 2023'
        },
        {
            'id': 2,
            'title': 'Выбор правовой формы для бизнеса в 2023 году',
            'description': 'Сравнение различных форм организации бизнеса - ИП, ООО, самозанятость и другие. Что выбрать в зависимости от вашей ситуации.',
            'category': 'Юридические вопросы',
            'image': url_for('static', filename='images/articles/legal-form.jpg'),
            'date': '2 июня 2023'
        },
        {
            'id': 3,
            'title': 'Маркетинговые стратегии с минимальным бюджетом',
            'description': 'Эффективные способы продвижения бизнеса без значительных финансовых вложений.',
            'category': 'Маркетинг',
            'image': url_for('static', filename='images/articles/marketing.jpg'),
            'date': '18 июня 2023'
        },
        {
            'id': 4,
            'title': 'Финансовый учет для начинающих предпринимателей',
            'description': 'Основы ведения финансового учета, которые должен знать каждый владелец бизнеса.',
            'category': 'Финансы',
            'image': url_for('static', filename='images/articles/finance.jpg'),
            'date': '5 июля 2023'
        },
        {
            'id': 5,
            'title': 'Как привлечь первых клиентов в новый бизнес',
            'description': 'Проверенные методы привлечения клиентов для только что открывшегося бизнеса.',
            'category': 'Маркетинг',
            'image': url_for('static', filename='images/articles/clients.jpg'),
            'date': '22 июля 2023'
        },
        {
            'id': 6,
            'title': 'Оптимизация налогообложения для малого бизнеса',
            'description': 'Законные способы снизить налоговую нагрузку на ваш бизнес.',
            'category': 'Налоги',
            'image': url_for('static', filename='images/articles/taxes.jpg'),
            'date': '10 августа 2023'
        }
    ]
    
    # Search functionality
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    
    filtered_articles = articles
    
    # Apply category filter if provided
    if category_filter:
        filtered_articles = [article for article in filtered_articles if 
                          article['category'] == category_filter]
    
    # Apply search filter if provided
    if search_query:
        filtered_articles = [article for article in filtered_articles if 
                          search_query.lower() in article['title'].lower() or 
                          search_query.lower() in article['description'].lower()]
    
    return render_template('knowledge_base.html', 
                          articles=filtered_articles, 
                          search_query=search_query,
                          category=category_filter)

@app.route('/knowledge-base/article/<int:article_id>')
def article_detail(article_id):
    # Mock data - in a real application, you would fetch from a database
    articles = {
        1: {
            'id': 1,
            'title': 'Как составить бизнес-план для малого бизнеса',
            'category': 'Планирование',
            'date': '15 мая 2023',
            'image': url_for('static', filename='images/articles/business-plan.jpg'),
            'content': """
                <h2>Введение</h2>
                <p>Бизнес-план является фундаментом любого успешного бизнеса. Этот документ не только помогает структурировать ваши мысли и идеи, но и служит инструментом для привлечения инвестиций и кредитов.</p>
                
                <h2>Что такое бизнес-план?</h2>
                <p>Бизнес-план — это документ, описывающий все основные аспекты будущего предприятия, анализирующий проблемы, с которыми оно может столкнуться, и определяющий способы решения этих проблем.</p>
                
                <h2>Структура бизнес-плана</h2>
                <p>Стандартный бизнес-план включает следующие разделы:</p>
                <ul>
                    <li><strong>Резюме</strong> — краткое описание проекта</li>
                    <li><strong>Описание компании</strong> — история, цели, миссия</li>
                    <li><strong>Анализ рынка</strong> — исследование отрасли, конкурентов, целевой аудитории</li>
                    <li><strong>Продукт или услуга</strong> — подробное описание</li>
                    <li><strong>Маркетинговый план</strong> — стратегии продвижения и продаж</li>
                    <li><strong>Операционный план</strong> — организационная структура, процессы</li>
                    <li><strong>Финансовый план</strong> — прогнозы доходов и расходов, точка безубыточности</li>
                    <li><strong>Приложения</strong> — дополнительные материалы</li>
                </ul>
                
                <h2>Резюме проекта</h2>
                <p>Несмотря на то, что резюме является первым разделом бизнес-плана, писать его рекомендуется в последнюю очередь, когда все остальные разделы уже готовы. В резюме должны быть отражены:</p>
                <ul>
                    <li>Название компании и вид деятельности</li>
                    <li>Миссия компании</li>
                    <li>Уникальное торговое предложение</li>
                    <li>Цели на ближайшие 1-3-5 лет</li>
                    <li>Краткая информация о команде</li>
                    <li>Объем необходимых инвестиций</li>
                    <li>Прогнозируемые финансовые показатели</li>
                </ul>
                
                <h2>Финансовый план</h2>
                <p>Этот раздел является одним из наиболее важных, поскольку он показывает, будет ли ваш бизнес прибыльным. Финансовый план должен включать:</p>
                <ul>
                    <li>Прогноз доходов и расходов</li>
                    <li>План движения денежных средств</li>
                    <li>Прогнозный баланс</li>
                    <li>Анализ точки безубыточности</li>
                    <li>Оценка эффективности инвестиций</li>
                </ul>
                
                <h2>Заключение</h2>
                <p>Бизнес-план — это не просто формальный документ, а инструмент, который поможет вам определить реалистичность вашей бизнес-идеи и спланировать шаги по ее реализации. Тщательно проработанный бизнес-план повышает шансы на успех вашего предприятия и помогает избежать типичных ошибок начинающих предпринимателей.</p>
            """,
            'related_articles': [2, 4, 5]
        },
        2: {
            'id': 2,
            'title': 'Выбор правовой формы для бизнеса в 2023 году',
            'category': 'Юридические вопросы',
            'date': '2 июня 2023',
            'image': url_for('static', filename='images/articles/legal-form.jpg'),
            'content': """
                <h2>Введение в правовые формы бизнеса</h2>
                <p>Выбор правовой формы является одним из первых и наиболее важных решений при открытии бизнеса. Этот выбор влияет на налогообложение, ответственность, возможности привлечения инвестиций и многие другие аспекты деятельности.</p>
                
                <h2>Основные формы ведения бизнеса</h2>
                <p>В России существует несколько основных форм ведения бизнеса:</p>
                
                <h3>Индивидуальный предприниматель (ИП)</h3>
                <p><strong>Преимущества:</strong></p>
                <ul>
                    <li>Простая и недорогая регистрация</li>
                    <li>Упрощенная отчетность</li>
                    <li>Возможность выбора различных систем налогообложения</li>
                    <li>Свободное распоряжение денежными средствами</li>
                </ul>
                <p><strong>Недостатки:</strong></p>
                <ul>
                    <li>Полная ответственность личным имуществом по обязательствам</li>
                    <li>Ограничения в видах деятельности</li>
                    <li>Сложности с привлечением инвестиций</li>
                    <li>Сложности с продажей бизнеса</li>
                </ul>
                
                <h3>Общество с ограниченной ответственностью (ООО)</h3>
                <p><strong>Преимущества:</strong></p>
                <ul>
                    <li>Ограниченная ответственность учредителей (в пределах стоимости долей)</li>
                    <li>Возможность привлечения инвестиций</li>
                    <li>Более высокий уровень доверия от контрагентов</li>
                    <li>Возможность продажи бизнеса</li>
                </ul>
                <p><strong>Недостатки:</strong></p>
                <ul>
                    <li>Более сложная и дорогая регистрация</li>
                    <li>Более сложная отчетность</li>
                    <li>Необходимость формирования уставного капитала</li>
                    <li>Ограничения в распоряжении средствами компании</li>
                </ul>
                
                <h3>Самозанятость</h3>
                <p>С 2019 года в России действует специальный налоговый режим для самозанятых граждан — налог на профессиональный доход (НПД).</p>
                <p><strong>Преимущества:</strong></p>
                <ul>
                    <li>Минимальная налоговая ставка (4% при работе с физлицами, 6% при работе с юрлицами)</li>
                    <li>Отсутствие необходимости подавать декларации</li>
                    <li>Нет обязательных страховых взносов</li>
                    <li>Простая регистрация через мобильное приложение</li>
                </ul>
                <p><strong>Недостатки:</strong></p>
                <ul>
                    <li>Ограничение по видам деятельности</li>
                    <li>Лимит годового дохода (2,4 млн рублей)</li>
                    <li>Невозможность нанимать сотрудников</li>
                    <li>Отсутствие стажа для пенсии (если не платить взносы добровольно)</li>
                </ul>
                
                <h2>Какую форму выбрать?</h2>
                <p>При выборе оптимальной правовой формы для вашего бизнеса учитывайте следующие факторы:</p>
                <ul>
                    <li>Масштаб планируемой деятельности</li>
                    <li>Количество учредителей</li>
                    <li>Потребность в привлечении инвестиций</li>
                    <li>Риски деятельности</li>
                    <li>Налоговые последствия</li>
                    <li>Отраслевые особенности</li>
                </ul>
                
                <h2>Заключение</h2>
                <p>Выбор правовой формы бизнеса — это стратегическое решение, которое должно соответствовать вашим долгосрочным целям. Рекомендуется проконсультироваться с юристом или налоговым консультантом перед принятием окончательного решения.</p>
            """,
            'related_articles': [1, 6]
        },
        # Additional articles would be defined similarly
    }
    
    article = articles.get(article_id)
    if not article:
        abort(404)
        
    # Get related articles
    related_articles = []
    if 'related_articles' in article:
        for rel_id in article['related_articles']:
            if rel_id in articles:
                related_articles.append(articles[rel_id])
    
    return render_template('article_detail.html', article=article, related_articles=related_articles)

# API для расчета стоимости бизнеса
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        print(f"Получен запрос на расчет: {data}")
        
        if not data:
            return jsonify({'error': 'Отсутствуют данные для расчета'}), 400
        
        if 'business_type' not in data or not data['business_type']:
            return jsonify({'error': 'Не указан тип бизнеса'}), 400
            
        if 'business_size' not in data or not data['business_size']:
            return jsonify({'error': 'Не указан размер бизнеса'}), 400
            
        price = calculate_price(data)
        return jsonify({'price': price})
    except Exception as e:
        print(f"Ошибка при расчете: {e}")
        print(traceback.format_exc())
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

# Страница результатов
@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        # Получаем данные из формы
        business_type_id = request.form.get('businessType')
        business_size_id = request.form.get('businessSize')
        
        # Получаем список выбранных функций
        features = request.form.getlist('features')
        
        # Получаем дополнительную информацию о выбранных опциях
        business_type_name = next((t['name'] for t in business_options['business_types'] if t['id'] == business_type_id), '')
        business_size_name = next((s['name'] for s in business_options['business_sizes'] if s['id'] == business_size_id), '')
        
        # Создаем данные для расчета
        data = {
            'business_type': business_type_id,
            'business_size': business_size_id,
            'features': features
        }
        
        # Рассчитываем цену
        price = calculate_price(data)
        
        # Сохраняем в сессию для отображения результата
        session['result'] = {
            'business_type': business_type_name,
            'business_size': business_size_name,
            'features': [f['name'] for f in business_options['features'] if f['id'] in features],
            'price': price
        }
        
        return redirect(url_for('result'))
    
    # Если это GET-запрос или после POST-запроса
    result_data = session.get('result', None)
    if not result_data:
        flash('Пожалуйста, сначала выполните расчет', 'warning')
        return redirect(url_for('constructor'))
    
    return render_template('result.html', result=result_data)

# Маршрут для скачивания PDF бизнес-плана
@app.route('/download-pdf')
def download_pdf():
    try:
        # Получаем данные результата из сессии
        result_data = session.get('result', None)
        if not result_data:
            print("Ошибка: данные результата не найдены в сессии")
            return make_response("Данные для создания PDF отсутствуют. Выполните расчет", 400)
        
        print(f"Полученные данные результата: {result_data}")
        
        # Проверяем, что все необходимые данные существуют
        required_fields = ['business_type', 'business_size', 'price']
        for field in required_fields:
            if field not in result_data:
                print(f"Ошибка: отсутствует поле {field} в данных результата")
                return make_response(f"Отсутствуют необходимые данные ({field}) для создания PDF", 400)
        
        # Генерируем PDF
        print("Начинаем генерацию PDF...")
        pdf_buffer = generate_pdf(result_data, business_options)
        
        # Проверяем, что буфер не пустой
        if not pdf_buffer or not hasattr(pdf_buffer, 'getvalue'):
            print("Ошибка: буфер PDF пуст или не является объектом BytesIO")
            return make_response("Не удалось создать PDF. Пустой буфер", 500)
        
        # Получаем байты PDF
        pdf_data = pdf_buffer.getvalue()
        if not pdf_data or len(pdf_data) < 100:
            print(f"Ошибка: PDF данные слишком малы, размер: {len(pdf_data) if pdf_data else 0} байт")
            if pdf_data and len(pdf_data) > 0:
                try:
                    error_text = pdf_data.decode('utf-8')
                    print(f"Содержимое буфера ошибки: {error_text}")
                except:
                    print("Не удалось декодировать содержимое буфера")
            return make_response("Ошибка при создании PDF. Результат слишком мал", 500)
        
        # Создаем HTTP-ответ
        response = make_response(pdf_data)
        
        # Устанавливаем заголовки
        # Используем транслитерацию для имени файла или простое латинское название
        clean_filename = f"business_plan_{result_data['business_type'].lower().replace(' ', '_').replace(',', '').replace('.', '')}"
        # Транслитеруем имя файла или используем ASCII версию
        safe_filename = "business_plan.pdf"
        if clean_filename.isascii():
            safe_filename = f"{clean_filename}.pdf"
        else:
            # Используем только ASCII-символы
            safe_filename = "business_plan.pdf"
        
        print(f"Исходное имя файла: {clean_filename}.pdf")
        print(f"Безопасное имя файла: {safe_filename}")
        
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
        response.headers['Content-Length'] = len(pdf_data)
        
        # Добавляем дополнительные заголовки для предотвращения кэширования
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        print(f"Размер PDF: {len(pdf_data)} байт")
        print(f"Отправка PDF с заголовками: {response.headers}")
        
        return response
    except Exception as e:
        print(f"Критическая ошибка при создании PDF: {e}")
        print(traceback.format_exc())
        return make_response(f"Произошла ошибка при создании PDF: {str(e)}", 500)

# Маршрут для получения кредитных ставок
@app.route('/api/bank-rates')
def get_bank_rates():
    try:
        # Получаем параметр force_refresh из запроса
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        
        # Получаем актуальные кредитные ставки
        rates = get_business_loan_rates(force_refresh)
        
        # Получаем средние ставки
        api = BankAPI()
        average_rates = api.get_average_rate()
        best_rate = api.get_best_rate()
        
        # Формируем ответ
        response_data = {
            'rates': rates,
            'average': average_rates,
            'best': best_rate
        }
        
        return make_response(json.dumps(response_data), 200, {'Content-Type': 'application/json'})
    except Exception as e:
        print(f"Ошибка при получении кредитных ставок: {e}")
        return make_response(json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'})

# Маршрут для расчета кредита
@app.route('/api/calculate-loan', methods=['POST'])
def calculate_loan():
    try:
        # Получаем данные из запроса
        loan_data = request.get_json()
        
        if not loan_data:
            return make_response(json.dumps({'error': 'Отсутствуют данные для расчета'}), 400, {'Content-Type': 'application/json'})
        
        # Получаем параметры кредита
        loan_amount = float(loan_data.get('loan_amount', 0))
        interest_rate = float(loan_data.get('interest_rate', 0))
        loan_term_years = float(loan_data.get('loan_term_years', 0))
        
        # Проверяем валидность данных
        if loan_amount <= 0 or interest_rate < 0 or loan_term_years <= 0:
            return make_response(json.dumps({'error': 'Некорректные параметры кредита'}), 400, {'Content-Type': 'application/json'})
        
        # Выполняем расчет
        result = calculate_business_loan(loan_amount, interest_rate, loan_term_years)
        
        return make_response(json.dumps(result), 200, {'Content-Type': 'application/json'})
    except Exception as e:
        print(f"Ошибка при расчете кредита: {e}")
        return make_response(json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'})

if __name__ == '__main__':
    app.run(debug=True) 