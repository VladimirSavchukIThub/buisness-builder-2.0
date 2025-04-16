from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from config import business_options, calculate_price
import traceback
import os
import locale

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

if __name__ == '__main__':
    app.run(debug=True) 