from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file, make_response
from config import business_options, calculate_price
import traceback
import os
import locale
from pdf_generator import generate_pdf
import urllib.parse

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

if __name__ == '__main__':
    app.run(debug=True) 