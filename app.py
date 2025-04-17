from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file, make_response, abort
from config import business_options, calculate_price, DATABASE_URI
import traceback
import os
import locale
from pdf_generator import generate_pdf
import urllib.parse
import json
from bank_api import get_business_loan_rates, calculate_business_loan, BankAPI
from chatbot import ChatBot  # Импортируем наш класс чат-бота
import jinja2
from markupsafe import Markup
from flask_migrate import Migrate
from models import db, BusinessType, BusinessSize, Feature, Article, Example, Message, User, BusinessPlan

# Импортируем модули для админ-панели
from admin_auth import verify_password, login_admin, logout_admin, is_admin_logged_in, admin_required
from data_manager import DataManager
from file_handler import save_file, delete_file
from datetime import datetime
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)  # для работы с сессиями и flash-сообщениями

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

# Инициализация чат-бота
chatbot = ChatBot()

# Инициализация менеджера данных (временно сохраняем для обратной совместимости)
data_manager = DataManager()

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

# Регистрируем фильтр nl2br для преобразования переносов строк в HTML теги <br>
@app.template_filter('nl2br')
def nl2br_filter(s):
    if s is None:
        return ''
    s = str(s).replace('\r\n', '\n').replace('\r', '\n')
    return Markup(s.replace('\n', '<br>'))

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
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    success_message = None
    
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        content = request.form.get('content')
        privacy = request.form.get('privacy')
        
        # Проверяем наличие всех необходимых данных
        if not all([name, email, subject, content, privacy]):
            flash('Пожалуйста, заполните все обязательные поля формы', 'danger')
            return render_template('contact.html')
        
        try:
            # Создаем новое сообщение в БД
            new_message = Message(
                name=name,
                email=email,
                subject=subject,
                content=content
            )
            db.session.add(new_message)
            db.session.commit()
            
            # Устанавливаем флаг успешной отправки
            success_message = True
            
            # Выводим сообщение об успешной отправке
            flash('Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.', 'success')
        except Exception as e:
            print(f"Ошибка при сохранении сообщения: {e}")
            flash('Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже.', 'danger')
    
    return render_template('contact.html', success_message=success_message)

# Страница с примерами успешных бизнес-моделей
@app.route('/examples')
def examples():
    return render_template('examples.html')

# Страница базы знаний
@app.route('/knowledge-base')
def knowledge_base():
    """Страница базы знаний."""
    # Получаем статьи из БД
    articles_query = Article.query
    
    # Search functionality
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    
    # Apply category filter if provided
    if category_filter:
        articles_query = articles_query.filter_by(category=category_filter)
    
    # Apply search filter if provided
    if search_query:
        search_pattern = f"%{search_query}%"
        articles_query = articles_query.filter(
            db.or_(
                Article.title.ilike(search_pattern),
                Article.description.ilike(search_pattern)
            )
        )
    
    # Получаем результаты
    articles = articles_query.all()
    
    return render_template('knowledge_base.html', 
                          articles=articles, 
                          search_query=search_query,
                          category=category_filter)

@app.route('/knowledge-base/article/<int:article_id>')
def article_detail(article_id):
    """Страница отдельной статьи."""
    article = Article.query.get_or_404(article_id)
    
    # Get related articles (for now, just get 2 random articles different from current)
    related_articles = Article.query.filter(Article.id != article_id).order_by(db.func.random()).limit(2).all()
    
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

# Маршрут для API чат-бота
@app.route('/api/chatbot', methods=['POST'])
def chat_api():
    try:
        # Получаем сообщение пользователя из запроса
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Отсутствует сообщение в запросе'}), 400
        
        user_message = data['message']
        print(f"Запрос к чат-боту: {user_message}")
        
        # Если это первое сообщение (пустое), возвращаем приветствие
        if not user_message.strip():
            return jsonify({'response': chatbot.get_greeting()})
        
        # Получаем ответ от чат-бота
        response = chatbot.get_response(user_message)
        
        return jsonify({'response': response})
    except Exception as e:
        print(f"Ошибка в работе чат-бота: {e}")
        print(traceback.format_exc())
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

# Маршруты для админ-панели

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Страница входа в админ-панель."""
    # Если администратор уже авторизован, перенаправляем на дашборд
    if is_admin_logged_in():
        return redirect(url_for('admin_dashboard'))
    
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if verify_password(username, password):
            login_admin(username)
            flash('Вы успешно вошли в систему', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Неверное имя пользователя или пароль'
    
    return render_template('admin/login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    """Выход из админ-панели."""
    logout_admin()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Главная страница админ-панели."""
    # Получаем данные для статистики из БД
    messages_count = Message.query.count()
    articles_count = Article.query.count()
    plans_count = BusinessPlan.query.count()
    users_count = User.query.count()
    
    # Данные для графика типов бизнеса (используем тестовые данные)
    top_business_types = [
        {'name': 'Интернет-магазин', 'count': 142},
        {'name': 'Кафе', 'count': 89},
        {'name': 'Салон красоты', 'count': 64},
        {'name': 'Строительство', 'count': 47},
        {'name': 'Другое', 'count': 4}
    ]
    
    # Генерируем тестовые данные для статистики
    stats = {
        'users_count': users_count,
        'articles_count': articles_count,
        'plans_count': plans_count,
        'messages_count': messages_count,
        
        # Данные для графика планов за 30 дней
        'days_labels': [f"{i+1}" for i in range(30)],
        'plans_by_day': [3, 5, 2, 4, 6, 5, 8, 7, 9, 12, 10, 8, 7, 11, 13, 9, 8, 10, 12, 14, 11, 9, 8, 7, 9, 11, 13, 10, 8, 12],
        
        # Данные для графика типов бизнеса
        'top_business_types': top_business_types,
        'top_business_types_names': [t['name'] for t in top_business_types],
        'top_business_types_counts': [t['count'] for t in top_business_types],
        'chart_colors': ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b']
    }
    
    # Получаем последние статьи и сообщения
    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()
    recent_messages = Message.query.order_by(Message.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_articles=recent_articles, recent_messages=recent_messages)

# Маршруты для управления типами бизнеса

@app.route('/admin/business-types')
@admin_required
def admin_business_types():
    """Список типов бизнеса."""
    business_types = data_manager.get_business_types()
    return render_template('admin/business_types/index.html', business_types=business_types)

@app.route('/admin/business-types/create', methods=['GET', 'POST'])
@admin_required
def admin_business_type_create():
    """Создание нового типа бизнеса."""
    if request.method == 'POST':
        name = request.form.get('name')
        base_price = int(request.form.get('base_price', 0))
        description = request.form.get('description', '')
        
        if not name:
            flash('Имя типа бизнеса не может быть пустым', 'danger')
            return render_template('admin/business_types/create.html')
        
        data_manager.add_business_type(name, base_price, description)
        flash('Тип бизнеса успешно создан', 'success')
        return redirect(url_for('admin_business_types'))
    
    return render_template('admin/business_types/create.html')

@app.route('/admin/business-types/edit/<type_id>', methods=['GET', 'POST'])
@admin_required
def admin_business_type_edit(type_id):
    """Редактирование типа бизнеса."""
    business_type = data_manager.get_business_type(type_id)
    if not business_type:
        flash('Тип бизнеса не найден', 'danger')
        return redirect(url_for('admin_business_types'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        base_price = int(request.form.get('base_price', 0))
        description = request.form.get('description', '')
        
        if not name:
            flash('Имя типа бизнеса не может быть пустым', 'danger')
            return render_template('admin/business_types/edit.html', business_type=business_type)
        
        data_manager.update_business_type(type_id, name, base_price, description)
        flash('Тип бизнеса успешно обновлен', 'success')
        return redirect(url_for('admin_business_types'))
    
    return render_template('admin/business_types/edit.html', business_type=business_type)

@app.route('/admin/business-types/delete/<type_id>', methods=['POST'])
@admin_required
def admin_business_type_delete(type_id):
    """Удаление типа бизнеса."""
    business_type = data_manager.get_business_type(type_id)
    if not business_type:
        flash('Тип бизнеса не найден', 'danger')
    else:
        data_manager.delete_business_type(type_id)
        flash('Тип бизнеса успешно удален', 'success')
    
    return redirect(url_for('admin_business_types'))

# Маршруты для управления дополнительными услугами (функциями)

@app.route('/admin/features')
@admin_required
def admin_features():
    """Список дополнительных услуг."""
    features = data_manager.get_features()
    return render_template('admin/features/index.html', features=features)

@app.route('/admin/features/create', methods=['GET', 'POST'])
@admin_required
def admin_feature_create():
    """Создание новой дополнительной услуги."""
    if request.method == 'POST':
        name = request.form.get('name')
        price = int(request.form.get('price', 0))
        description = request.form.get('description', '')
        
        if not name:
            flash('Название услуги не может быть пустым', 'danger')
            return render_template('admin/features/create.html')
        
        data_manager.add_feature(name, price, description)
        flash('Дополнительная услуга успешно создана', 'success')
        return redirect(url_for('admin_features'))
    
    return render_template('admin/features/create.html')

@app.route('/admin/features/edit/<feature_id>', methods=['GET', 'POST'])
@admin_required
def admin_feature_edit(feature_id):
    """Редактирование дополнительной услуги."""
    feature = data_manager.get_feature(feature_id)
    if not feature:
        flash('Дополнительная услуга не найдена', 'danger')
        return redirect(url_for('admin_features'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        price = int(request.form.get('price', 0))
        description = request.form.get('description', '')
        
        if not name:
            flash('Название услуги не может быть пустым', 'danger')
            return render_template('admin/features/edit.html', feature=feature)
        
        data_manager.update_feature(feature_id, name, price, description)
        flash('Дополнительная услуга успешно обновлена', 'success')
        return redirect(url_for('admin_features'))
    
    return render_template('admin/features/edit.html', feature=feature)

@app.route('/admin/features/delete/<feature_id>', methods=['POST'])
@admin_required
def admin_feature_delete(feature_id):
    """Удаление дополнительной услуги."""
    feature = data_manager.get_feature(feature_id)
    if not feature:
        flash('Дополнительная услуга не найдена', 'danger')
    else:
        data_manager.delete_feature(feature_id)
        flash('Дополнительная услуга успешно удалена', 'success')
    
    return redirect(url_for('admin_features'))

# Маршруты для управления примерами успешных бизнес-проектов

@app.route('/admin/examples')
@admin_required
def admin_examples():
    """Список примеров бизнес-проектов."""
    examples = data_manager.get_examples()
    return render_template('admin/examples/index.html', examples=examples)

@app.route('/admin/examples/create', methods=['GET', 'POST'])
@admin_required
def admin_example_create():
    """Создание нового примера бизнес-проекта."""
    if request.method == 'POST':
        title = request.form.get('title')
        business_type = request.form.get('business_type')
        investment = request.form.get('investment')
        profit = request.form.get('profit')
        period = request.form.get('period')
        content = request.form.get('content')
        
        # Обработка загрузки изображения
        image = ''
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename:
                image = save_file(image_file, 'images/examples')
        
        if not title or not business_type:
            flash('Заполните обязательные поля', 'danger')
            return render_template('admin/examples/create.html')
        
        data_manager.add_example(title, business_type, investment, profit, period, content, image)
        flash('Пример бизнес-проекта успешно создан', 'success')
        return redirect(url_for('admin_examples'))
    
    return render_template('admin/examples/create.html')

@app.route('/admin/examples/edit/<example_id>', methods=['GET', 'POST'])
@admin_required
def admin_example_edit(example_id):
    """Редактирование примера бизнес-проекта."""
    example = data_manager.get_example(example_id)
    if not example:
        flash('Пример бизнес-проекта не найден', 'danger')
        return redirect(url_for('admin_examples'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        business_type = request.form.get('business_type')
        investment = request.form.get('investment')
        profit = request.form.get('profit')
        period = request.form.get('period')
        content = request.form.get('content')
        
        # Обработка изображения
        image = example.get('image', '')
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename:
                # Удаляем старое изображение
                if image:
                    delete_file(image)
                # Сохраняем новое изображение
                image = save_file(image_file, 'images/examples')
        
        if not title or not business_type:
            flash('Заполните обязательные поля', 'danger')
            return render_template('admin/examples/edit.html', example=example)
        
        data_manager.update_example(example_id, title, business_type, investment, profit, period, content, image)
        flash('Пример бизнес-проекта успешно обновлен', 'success')
        return redirect(url_for('admin_examples'))
    
    return render_template('admin/examples/edit.html', example=example)

@app.route('/admin/examples/delete/<example_id>', methods=['POST'])
@admin_required
def admin_example_delete(example_id):
    """Удаление примера бизнес-проекта."""
    example = data_manager.get_example(example_id)
    if not example:
        flash('Пример бизнес-проекта не найден', 'danger')
    else:
        # Удаляем связанное изображение
        if example.get('image'):
            delete_file(example['image'])
        
        data_manager.delete_example(example_id)
        flash('Пример бизнес-проекта успешно удален', 'success')
    
    return redirect(url_for('admin_examples'))

# Маршруты для управления статьями базы знаний

@app.route('/admin/articles')
@admin_required
def admin_articles():
    """Список статей."""
    articles = Article.query.all()
    return render_template('admin/articles/index.html', articles=articles)

@app.route('/admin/articles/create', methods=['GET', 'POST'])
@admin_required
def admin_article_create():
    """Создание новой статьи."""
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        content = request.form.get('content')
        featured = True if request.form.get('featured') else False
        
        if not title or not category or not description:
            flash('Заполните обязательные поля', 'danger')
            return render_template('admin/articles/create.html')
        
        # Обработка загрузки изображения
        image = ''
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename:
                image = save_file(image_file, 'images/articles')
        
        # Форматируем дату публикации
        date = datetime.now().strftime('%d %B %Y')
        
        # Создаем новую статью
        new_article = Article(
            title=title,
            category=category,
            description=description,
            content=content,
            image=image,
            date=date,
            featured=featured
        )
        
        db.session.add(new_article)
        db.session.commit()
        
        flash('Статья успешно создана', 'success')
        return redirect(url_for('admin_articles'))
    
    return render_template('admin/articles/create.html')

@app.route('/admin/articles/edit/<article_id>', methods=['GET', 'POST'])
@admin_required
def admin_article_edit(article_id):
    """Редактирование статьи."""
    article = Article.query.get_or_404(article_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        content = request.form.get('content')
        featured = True if request.form.get('featured') else False
        
        if not title or not category or not description:
            flash('Заполните обязательные поля', 'danger')
            return render_template('admin/articles/edit.html', article=article)
        
        # Обработка изображения
        image = article.image
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename:
                # Удаляем старое изображение если оно есть
                if image:
                    delete_file(image)
                # Сохраняем новое изображение
                image = save_file(image_file, 'images/articles')
        
        # Проверяем, нужно ли удалить изображение
        if request.form.get('delete_image') and image:
            delete_file(image)
            image = ''
        
        # Обновляем данные статьи
        article.title = title
        article.category = category
        article.description = description
        article.content = content
        article.image = image
        article.featured = featured
        
        db.session.commit()
        flash('Статья успешно обновлена', 'success')
        return redirect(url_for('admin_articles'))
    
    return render_template('admin/articles/edit.html', article=article)

@app.route('/admin/articles/delete/<article_id>', methods=['POST'])
@admin_required
def admin_article_delete(article_id):
    """Удаление статьи."""
    article = Article.query.get_or_404(article_id)
    
    # Удаляем связанное изображение
    if article.image:
        delete_file(article.image)
    
    db.session.delete(article)
    db.session.commit()
    flash('Статья успешно удалена', 'success')
    
    return redirect(url_for('admin_articles'))

# Маршруты для управления сообщениями от пользователей

@app.route('/admin/messages')
@admin_required
def admin_messages():
    """Список сообщений от пользователей."""
    # Получаем все сообщения, сначала непрочитанные, потом по дате (новые вначале)
    messages = Message.query.order_by(Message.is_read, Message.created_at.desc()).all()
    return render_template('admin/messages/index.html', messages=messages)

@app.route('/admin/messages/<message_id>')
@admin_required
def admin_message_view(message_id):
    """Просмотр сообщения от пользователя."""
    message = Message.query.get_or_404(message_id)
    
    # Отмечаем сообщение как прочитанное, если оно не прочитано
    if not message.is_read:
        message.is_read = True
        db.session.commit()
    
    return render_template('admin/messages/view.html', message=message)

@app.route('/admin/messages/delete/<message_id>', methods=['POST'])
@admin_required
def admin_message_delete(message_id):
    """Удаление сообщения."""
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Сообщение успешно удалено', 'success')
    
    return redirect(url_for('admin_messages'))

# Маршруты для управления пользователями

@app.route('/admin/users')
@admin_required
def admin_users():
    """Страница управления пользователями."""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/create', methods=['GET', 'POST'])
@admin_required
def admin_user_create():
    """Создание нового пользователя."""
    if request.method == 'POST':
        # Получаем данные формы
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        is_admin = bool(request.form.get('is_admin'))
        
        # Проверяем обязательные поля
        if not name or not email or not password:
            flash('Все поля должны быть заполнены', 'danger')
            return redirect(url_for('admin_user_create'))
            
        # Проверяем уникальность email
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'danger')
            return redirect(url_for('admin_user_create'))
        
        # Создаем пользователя
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            is_admin=is_admin
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Пользователь успешно создан', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании пользователя: {str(e)}', 'danger')
            
    return render_template('admin/user_form.html', user=None, action='create')

@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_user_edit(user_id):
    """Редактирование пользователя."""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Получаем данные формы
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        is_admin = bool(request.form.get('is_admin'))
        
        # Проверяем обязательные поля
        if not name or not email:
            flash('Имя и email должны быть заполнены', 'danger')
            return redirect(url_for('admin_user_edit', user_id=user_id))
            
        # Проверяем уникальность email (исключая текущего пользователя)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            flash('Пользователь с таким email уже существует', 'danger')
            return redirect(url_for('admin_user_edit', user_id=user_id))
        
        # Обновляем пользователя
        user.name = name
        user.email = email
        user.is_admin = is_admin
        
        # Обновляем пароль только если он был предоставлен
        if password:
            user.password = generate_password_hash(password)
        
        try:
            db.session.commit()
            flash('Пользователь успешно обновлен', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении пользователя: {str(e)}', 'danger')
            
    return render_template('admin/user_form.html', user=user, action='edit')

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_user_delete(user_id):
    """Удаление пользователя."""
    user = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении пользователя: {str(e)}', 'danger')
        
    return redirect(url_for('admin_users'))

# Маршрут для настроек

@app.route('/admin/settings')
@admin_required
def admin_settings():
    """Настройки приложения."""
    return render_template('admin/settings.html')

if __name__ == '__main__':
    app.run(debug=True)

# CLI команды для управления базой данных
@app.cli.command("init-db")
def init_db():
    """Инициализирует базу данных."""
    db.create_all()
    print("База данных инициализирована.")

@app.cli.command("migrate-data")
def migrate_data():
    """Миграция данных из JSON файлов в базу данных."""
    # Импорт бизнес-типов
    business_types = data_manager.get_business_types()
    for bt in business_types:
        existing = BusinessType.query.filter_by(name=bt['name']).first()
        if not existing:
            new_bt = BusinessType(
                name=bt['name'],
                base_price=bt['base_price'],
                description=bt.get('description', '')
            )
            db.session.add(new_bt)
    
    # Импорт функций/услуг
    features = data_manager.get_features()
    for f in features:
        existing = Feature.query.filter_by(name=f['name']).first()
        if not existing:
            new_feature = Feature(
                name=f['name'],
                price=f['price'],
                description=f.get('description', '')
            )
            db.session.add(new_feature)
    
    # Импорт бизнес-размеров из конфигурации
    for bs in business_options['business_sizes']:
        existing = BusinessSize.query.filter_by(name=bs['name']).first()
        if not existing:
            new_bs = BusinessSize(
                name=bs['name'],
                multiplier=bs['multiplier'],
                description=bs.get('description', '')
            )
            db.session.add(new_bs)
    
    # Импорт статей
    articles = data_manager.get_articles()
    for a in articles:
        existing = Article.query.filter_by(title=a['title']).first()
        if not existing:
            new_article = Article(
                title=a['title'],
                category=a['category'],
                description=a['description'],
                content=a['content'],
                image=a.get('image', ''),
                date=a.get('date', ''),
                featured=a.get('featured', False)
            )
            db.session.add(new_article)
    
    # Импорт примеров
    examples = data_manager.get_examples()
    for e in examples:
        existing = Example.query.filter_by(title=e['title']).first()
        if not existing:
            new_example = Example(
                title=e['title'],
                business_type=e['business_type'],
                investment=e['investment'],
                profit=e['profit'],
                period=e['period'],
                content=e['content'],
                image=e.get('image', '')
            )
            db.session.add(new_example)
    
    # Импорт сообщений
    messages = data_manager.get_messages()
    for m in messages:
        existing = Message.query.filter_by(
            name=m['name'], 
            email=m['email'],
            created_at=datetime.strptime(m['created_at'], '%d.%m.%Y %H:%M:%S') if isinstance(m['created_at'], str) else m['created_at']
        ).first()
        if not existing:
            new_message = Message(
                name=m['name'],
                email=m['email'],
                subject=m['subject'],
                content=m['content'],
                is_read=m.get('is_read', False)
            )
            db.session.add(new_message)
    
    # Создание администратора, если его нет
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin_hash = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'  # sha256 хеш для 'admin'
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=admin_hash,
            is_admin=True
        )
        db.session.add(admin)
    
    db.session.commit()
    print("Данные успешно перенесены из JSON в базу данных.") 