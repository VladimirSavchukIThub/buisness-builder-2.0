import os
import io
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Для работы без графического интерфейса
import matplotlib.font_manager as fm

# Добавляем поддержку кириллических шрифтов
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Путь к системным шрифтам
FONT_PATH = os.path.join(os.environ.get('SYSTEMROOT', ''), 'Fonts')

# Настройка шрифтов для matplotlib
ARIAL_PATH = os.path.join(FONT_PATH, 'arial.ttf')
if os.path.exists(ARIAL_PATH):
    # Добавляем шрифт Arial в matplotlib
    fm.fontManager.addfont(ARIAL_PATH)
    matplotlib.rcParams['font.family'] = 'Arial'
else:
    # Если Arial недоступен, используем другие шрифты из семейства sans-serif
    matplotlib.rcParams['font.family'] = 'sans-serif'
    
# Дополнительные настройки matplotlib для поддержки кириллицы
matplotlib.rcParams['axes.unicode_minus'] = False

class PDFGenerator:
    def __init__(self):
        # Регистрируем шрифты с поддержкой кириллицы
        self._register_fonts()
        
        self.styles = getSampleStyleSheet()
        
        # Проверяем наличие стилей перед добавлением
        if 'Heading1Custom' not in self.styles:
            self.styles.add(ParagraphStyle(name='Heading1Custom', 
                                         fontName='Arial-Bold', 
                                         fontSize=16, 
                                         leading=20,
                                         spaceAfter=10))
        if 'Heading2Custom' not in self.styles:
            self.styles.add(ParagraphStyle(name='Heading2Custom', 
                                         fontName='Arial-Bold', 
                                         fontSize=14, 
                                         leading=18,
                                         spaceBefore=10,
                                         spaceAfter=6))
        if 'BodyTextCustom' not in self.styles:
            self.styles.add(ParagraphStyle(name='BodyTextCustom', 
                                         fontName='Arial', 
                                         fontSize=12, 
                                         leading=16,
                                         spaceBefore=4,
                                         spaceAfter=4))
    
    def _register_fonts(self):
        """Регистрирует системные шрифты с поддержкой кириллицы"""
        try:
            # Регистрируем Arial, который есть в большинстве Windows систем
            arial_path = os.path.join(FONT_PATH, 'arial.ttf')
            arial_bold_path = os.path.join(FONT_PATH, 'arialbd.ttf')
            
            if os.path.exists(arial_path):
                pdfmetrics.registerFont(TTFont('Arial', arial_path))
                print("Шрифт Arial успешно зарегистрирован")
            else:
                print(f"Шрифт не найден: {arial_path}")
            
            if os.path.exists(arial_bold_path):
                pdfmetrics.registerFont(TTFont('Arial-Bold', arial_bold_path))
                print("Шрифт Arial-Bold успешно зарегистрирован")
            else:
                print(f"Шрифт не найден: {arial_bold_path}")
                
        except Exception as e:
            print(f"Ошибка при регистрации шрифтов: {e}")
            # Если не удалось зарегистрировать шрифты, используем стандартные
    
    def _format_number(self, number):
        """Форматирует число, добавляя пробелы в качестве разделителей тысяч"""
        return "{:,}".format(number).replace(',', ' ')
    
    def _to_utf8(self, text):
        """Преобразует текст в кодировку UTF-8 для корректного отображения кириллицы"""
        if isinstance(text, str):
            return text
        try:
            return text.decode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            return str(text)
    
    def _create_pie_chart(self, data, labels, title="Структура расходов"):
        """Создает круговую диаграмму с использованием matplotlib"""
        try:
            # Сбрасываем настройки графика
            plt.rcdefaults()
            
            # Создаем график с кириллическими шрифтами
            plt.figure(figsize=(8, 6), dpi=100)
            
            # Используем патч для текста, чтобы избежать проблем с кодировкой
            for i, label in enumerate(labels):
                # Ограничиваем длину метки
                if len(label) > 15:
                    labels[i] = label[:15] + '...'
            
            # Создаем график
            patches, texts, autotexts = plt.pie(
                data, 
                labels=None,  # Сначала не добавляем метки
                autopct='%1.1f%%', 
                startangle=90, 
                shadow=True,
                textprops={'fontsize': 10}
            )
            
            # Добавляем метки отдельно с более точным контролем
            plt.legend(patches, labels, loc="best", fontsize=9)
            
            plt.axis('equal')
            plt.title(title, fontsize=12)
            
            # Сохраняем диаграмму во временный буфер
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        except Exception as e:
            print(f"Ошибка при создании круговой диаграммы: {e}")
            # Создаем пустую диаграмму в случае ошибки
            empty_buffer = io.BytesIO()
            plt.figure(figsize=(1, 1))
            plt.text(0.5, 0.5, "Ошибка создания диаграммы", ha='center', va='center')
            plt.savefig(empty_buffer, format='png')
            empty_buffer.seek(0)
            plt.close()
            return empty_buffer
    
    def _create_bar_chart(self, data, labels, title="Сравнение по размерам бизнеса"):
        """Создает столбчатую диаграмму с использованием matplotlib"""
        try:
            # Сбрасываем настройки графика
            plt.rcdefaults()
            
            # Создаем график с кириллическими шрифтами
            plt.figure(figsize=(8, 5), dpi=100)
            
            # Используем метки для названий столбцов
            x_pos = range(len(labels))
            
            # Создаем столбчатый график
            plt.bar(x_pos, data, align='center')
            plt.xticks(x_pos, labels)
            
            plt.title(title, fontsize=12)
            plt.ylabel('Стоимость (руб.)', fontsize=10)
            
            # Форматируем значения осей
            plt.gca().get_yaxis().set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' '))
            )
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Сохраняем диаграмму во временный буфер
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        except Exception as e:
            print(f"Ошибка при создании столбчатой диаграммы: {e}")
            # Создаем пустую диаграмму в случае ошибки
            empty_buffer = io.BytesIO()
            plt.figure(figsize=(1, 1))
            plt.text(0.5, 0.5, "Ошибка создания диаграммы", ha='center', va='center')
            plt.savefig(empty_buffer, format='png')
            empty_buffer.seek(0)
            plt.close()
            return empty_buffer
    
    def generate_business_plan_pdf(self, result_data, business_options):
        """Генерирует PDF файл бизнес-плана на основе данных расчета"""
        try:
            print("Начинаем генерацию PDF")
            print(f"Получены данные: {result_data}")
            
            # Создаем буфер для PDF
            buffer = io.BytesIO()
            
            # Создаем PDF документ
            doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
            
            # Список элементов для размещения на странице
            elements = []
            
            # Обрабатываем текст для корректного отображения в PDF
            business_type = result_data['business_type']
            business_size = result_data['business_size']
            price = result_data['price']
            
            # Заголовок документа
            elements.append(Paragraph(f"Бизнес-план: {business_type}", self.styles['Heading1Custom']))
            elements.append(Spacer(1, 0.5*cm))
            
            # Основная информация
            elements.append(Paragraph("Основная информация", self.styles['Heading2Custom']))
            elements.append(Paragraph(f"<b>Тип бизнеса:</b> {business_type}", self.styles['BodyTextCustom']))
            elements.append(Paragraph(f"<b>Размер бизнеса:</b> {business_size}", self.styles['BodyTextCustom']))
            elements.append(Paragraph(f"<b>Итоговая стоимость:</b> {self._format_number(price)} руб.", self.styles['BodyTextCustom']))
            elements.append(Spacer(1, 0.5*cm))
            
            # Таблица выбранных функций
            if result_data.get('features', []):
                print("Обрабатываем выбранные функции")
                elements.append(Paragraph("Выбранные функции", self.styles['Heading2Custom']))
                
                # Данные для таблицы - проходим по всем возможным функциям и находим те, которые выбраны
                feature_data = [["Функция", "Стоимость"]]
                feature_costs = []
                feature_names = []
                
                for feature in business_options['features']:
                    # Проверяем, если имя этой функции есть в выбранных функциях результата
                    if feature['name'] in result_data['features']:
                        feature_data.append([feature['name'], f"{self._format_number(feature['price'])} руб."])
                        feature_costs.append(feature['price'])
                        feature_names.append(feature['name'])
                        print(f"Добавлена функция: {feature['name']}, цена: {feature['price']}")
                
                # Создание таблицы если есть данные
                if len(feature_data) > 1:
                    features_table = Table(feature_data, colWidths=[doc.width*0.7, doc.width*0.3])
                    features_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (1, 0), 'Arial-Bold'),
                        ('FONTSIZE', (0, 0), (1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (1, 0), 6),
                        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ]))
                    elements.append(features_table)
                    elements.append(Spacer(1, 0.5*cm))
                    
                    # Круговая диаграмма для функций
                    if len(feature_costs) > 0:
                        elements.append(Paragraph("Распределение расходов по функциям", self.styles['Heading2Custom']))
                        
                        try:
                            print(f"Создаем круговую диаграмму с данными: {feature_costs}, названия: {feature_names}")
                            pie_img_buffer = self._create_pie_chart(
                                feature_costs, 
                                feature_names,
                                "Структура расходов на дополнительные функции"
                            )
                            
                            pie_img = Image(pie_img_buffer, width=400, height=300)
                            elements.append(pie_img)
                            elements.append(Spacer(1, 0.5*cm))
                            print("Круговая диаграмма создана успешно")
                        except Exception as e:
                            print(f"Ошибка при создании круговой диаграммы: {e}")
                            # Если не удается создать диаграмму, добавляем текстовое описание
                            elements.append(Paragraph("Не удалось сгенерировать диаграмму", self.styles['BodyTextCustom']))
                            elements.append(Spacer(1, 0.5*cm))
                else:
                    elements.append(Paragraph("Информация о функциях недоступна", self.styles['BodyTextCustom']))
                    elements.append(Spacer(1, 0.5*cm))
            else:
                elements.append(Paragraph("Дополнительные функции не выбраны", self.styles['BodyTextCustom']))
                elements.append(Spacer(1, 0.5*cm))
            
            # Сравнение расходов по размерам бизнеса
            elements.append(Paragraph("Сравнение стоимости по размерам бизнеса", self.styles['Heading2Custom']))
            
            # Находим тип бизнеса по имени
            print(f"Ищем тип бизнеса по имени: {result_data['business_type']}")
            business_type_id = None
            for bt in business_options['business_types']:
                if bt['name'] == result_data['business_type']:
                    business_type_id = bt['id']
                    print(f"Найден идентификатор типа бизнеса: {business_type_id}")
                    break
            
            if business_type_id:
                # Находим базовую цену
                base_price = 0
                for bt in business_options['business_types']:
                    if bt['id'] == business_type_id:
                        base_price = bt['base_price']
                        print(f"Найдена базовая цена: {base_price}")
                        break
                
                # Рассчитываем стоимость для разных размеров
                try:
                    size_data = []
                    size_labels = []
                    
                    for size in business_options['business_sizes']:
                        price = base_price * size['multiplier']
                        size_data.append(price)
                        size_labels.append(f"{size['name']}")
                    
                    print(f"Данные для столбчатой диаграммы: {size_data}, метки: {size_labels}")
                    
                    bar_img_buffer = self._create_bar_chart(
                        size_data,
                        size_labels,
                        f"Сравнение стоимости {business_type} по размерам"
                    )
                    
                    bar_img = Image(bar_img_buffer, width=400, height=250)
                    elements.append(bar_img)
                    elements.append(Spacer(1, 0.5*cm))
                    print("Столбчатая диаграмма создана успешно")
                except Exception as e:
                    print(f"Ошибка при создании столбчатой диаграммы: {e}")
                    # Если не удается создать диаграмму, добавляем текстовое описание
                    elements.append(Paragraph("Не удалось сгенерировать диаграмму сравнения", self.styles['BodyTextCustom']))
                    elements.append(Spacer(1, 0.5*cm))
            else:
                elements.append(Paragraph("Информация о типе бизнеса недоступна для сравнения", self.styles['BodyTextCustom']))
                elements.append(Spacer(1, 0.5*cm))
            
            # Детализация расходов
            elements.append(Paragraph("Детализация расходов", self.styles['Heading2Custom']))
            
            # Рассчитываем разбивку стоимости, если она не предоставлена
            total_price = result_data['price']
            cost_breakdown = result_data.get('cost_breakdown', None)
            
            if not cost_breakdown:
                # Используем стандартное распределение затрат
                cost_breakdown = {
                    "Оборудование и техника": round(total_price * 0.35),
                    "Аренда помещения": round(total_price * 0.15),
                    "Персонал и зарплаты": round(total_price * 0.25),
                    "Маркетинг и реклама": round(total_price * 0.10),
                }
                # Вычисляем прочие расходы, чтобы сумма совпадала с общей стоимостью
                other_costs = total_price - sum(cost_breakdown.values())
                cost_breakdown["Прочие расходы"] = other_costs
            
            # Создаем таблицу разбивки расходов
            cost_data = [["Категория затрат", "Сумма (руб.)", "Доля (%)"]]
            
            # Добавляем данные в таблицу
            for category, amount in cost_breakdown.items():
                percentage = round((amount / total_price) * 100, 1)
                cost_data.append([category, f"{self._format_number(amount)}", f"{percentage}%"])
            
            # Добавляем строку с итогами
            cost_data.append(["Итого", f"{self._format_number(total_price)}", "100%"])
            
            # Создаем таблицу
            cost_table = Table(cost_data, colWidths=[doc.width*0.5, doc.width*0.3, doc.width*0.2])
            cost_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (2, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (2, 0), 'Arial-Bold'),
                ('FONTSIZE', (0, 0), (2, 0), 12),
                ('BOTTOMPADDING', (0, 0), (2, 0), 6),
                ('ALIGN', (1, 1), (2, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Arial-Bold'),
            ]))
            elements.append(cost_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # Добавляем круговую диаграмму для расходов
            try:
                pie_categories = list(cost_breakdown.keys())
                pie_values = list(cost_breakdown.values())
                
                print(f"Создание круговой диаграммы расходов: {pie_values}, {pie_categories}")
                cost_pie_buffer = self._create_pie_chart(
                    pie_values,
                    pie_categories,
                    "Структура расходов по категориям"
                )
                
                cost_pie_img = Image(cost_pie_buffer, width=400, height=300)
                elements.append(cost_pie_img)
                elements.append(Spacer(1, 0.5*cm))
                print("Круговая диаграмма расходов создана успешно")
            except Exception as e:
                print(f"Ошибка при создании круговой диаграммы расходов: {e}")
                # Если не удается создать диаграмму, добавляем текстовое описание
                elements.append(Paragraph("Не удалось сгенерировать диаграмму распределения расходов", self.styles['BodyTextCustom']))
                elements.append(Spacer(1, 0.5*cm))
            
            # Описание категорий расходов
            elements.append(Paragraph("Пояснения к категориям расходов:", self.styles['BodyTextCustom']))
            elements.append(Spacer(1, 0.3*cm))
            
            category_explanations = [
                "<b>Оборудование и техника</b> - включает стоимость необходимого оборудования, компьютерной техники, мебели и других материальных активов.",
                "<b>Аренда помещения</b> - расходы на аренду и подготовку помещения для бизнеса.",
                "<b>Персонал и зарплаты</b> - затраты на наём и оплату труда сотрудников в первые месяцы работы.",
                "<b>Маркетинг и реклама</b> - бюджет на маркетинговые мероприятия, рекламу и продвижение.",
                "<b>Прочие расходы</b> - включают административные расходы, юридические услуги, страхование и прочие затраты."
            ]
            
            for explanation in category_explanations:
                elements.append(Paragraph(explanation, self.styles['BodyTextCustom']))
            
            elements.append(Spacer(1, 0.5*cm))
            
            # Прогнозирование окупаемости инвестиций
            elements.append(Paragraph("Прогноз окупаемости инвестиций", self.styles['Heading2Custom']))
            elements.append(Spacer(1, 0.3*cm))
            
            # Рассчитываем показатели окупаемости
            total_investment = result_data['price']
            monthly_revenue = round(total_investment * 0.15)  # Примерно 15% от инвестиций
            monthly_expenses = round(monthly_revenue * 0.7)   # Примерно 70% от выручки
            monthly_profit = monthly_revenue - monthly_expenses
            months_to_roi = round(total_investment / monthly_profit) if monthly_profit > 0 else "N/A"
            annual_roi = round((monthly_profit * 12 / total_investment) * 100) if monthly_profit > 0 else "N/A"
            
            # Создаем таблицу с показателями
            roi_data = [
                ["Показатель", "Значение"],
                ["Общие инвестиции", f"{self._format_number(total_investment)} руб."],
                ["Прогнозируемый ежемесячный доход", f"{self._format_number(monthly_revenue)} руб."],
                ["Прогнозируемые ежемесячные расходы", f"{self._format_number(monthly_expenses)} руб."],
                ["Прогнозируемая ежемесячная прибыль", f"{self._format_number(monthly_profit)} руб."],
                ["Расчетный срок окупаемости", f"{months_to_roi} месяцев"],
                ["Прогнозируемая годовая доходность (ROI)", f"{annual_roi}%"]
            ]
            
            roi_table = Table(roi_data, colWidths=[doc.width*0.6, doc.width*0.4])
            roi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Arial-Bold'),
                ('FONTSIZE', (0, 0), (1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (1, 0), 6),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('BACKGROUND', (0, 4), (-1, 4), colors.lightblue),  # Выделяем строку окупаемости
                ('FONTNAME', (0, 4), (1, 4), 'Arial-Bold'),
            ]))
            elements.append(roi_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # Создаем график окупаемости (линейная диаграмма)
            try:
                # Создаем данные для графика окупаемости
                months = list(range(1, months_to_roi + 7)) if isinstance(months_to_roi, int) else list(range(1, 19))
                cumulative_profit = [monthly_profit * month - total_investment for month in months]
                
                # Сбрасываем настройки графика
                plt.rcdefaults()
                plt.figure(figsize=(8, 5), dpi=100)
                
                # Строим график
                plt.plot(months, cumulative_profit, marker='o', linestyle='-', color='blue', linewidth=2)
                plt.axhline(y=0, color='r', linestyle='--')  # Линия нулевой прибыли (точка окупаемости)
                
                # Настраиваем оси и подписи
                plt.title('Прогноз окупаемости инвестиций', fontsize=12)
                plt.xlabel('Месяцы', fontsize=10)
                plt.ylabel('Прибыль/Убыток (руб.)', fontsize=10)
                plt.grid(True, linestyle='--', alpha=0.7)
                
                # Добавляем подпись точки окупаемости, если она есть
                if isinstance(months_to_roi, int):
                    plt.annotate(f'Точка окупаемости\n({months_to_roi} месяцев)',
                                xy=(months_to_roi, 0), xytext=(months_to_roi+1, monthly_profit*2),
                                arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='green'),
                                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="green", alpha=0.8))
                
                # Форматируем значения осей
                plt.gca().get_yaxis().set_major_formatter(
                    matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' '))
                )
                
                plt.tight_layout()
                
                # Сохраняем график во временный буфер
                roi_chart_buffer = io.BytesIO()
                plt.savefig(roi_chart_buffer, format='png', bbox_inches='tight')
                roi_chart_buffer.seek(0)
                plt.close()
                
                # Добавляем график в PDF
                roi_chart_img = Image(roi_chart_buffer, width=450, height=250)
                elements.append(roi_chart_img)
                elements.append(Spacer(1, 0.5*cm))
                print("График окупаемости создан успешно")
            except Exception as e:
                print(f"Ошибка при создании графика окупаемости: {e}")
                elements.append(Paragraph("Не удалось сгенерировать график окупаемости", self.styles['BodyTextCustom']))
                elements.append(Spacer(1, 0.5*cm))
            
            # Добавляем предупреждение
            elements.append(Paragraph("Важное примечание:", self.styles['BodyTextCustom']))
            elements.append(Paragraph(
                "Представленный прогноз окупаемости основан на среднерыночных показателях и предназначен для предварительной оценки. "
                "Фактический срок окупаемости может существенно отличаться в зависимости от множества факторов, включая:",
                self.styles['BodyTextCustom']
            ))
            
            # Список факторов, влияющих на окупаемость
            factors = [
                "Расположение бизнеса и проходимость",
                "Эффективность маркетинговых мероприятий",
                "Сезонность и колебания спроса",
                "Конкурентная ситуация на рынке",
                "Экономическая ситуация в регионе"
            ]
            
            for factor in factors:
                elements.append(Paragraph(f"• {factor}", self.styles['BodyTextCustom']))
            
            elements.append(Spacer(1, 0.5*cm))
            
            # Рекомендации
            elements.append(Paragraph("Рекомендации", self.styles['Heading2Custom']))
            
            recommendations = [
                ["Параметр", "Рекомендация"],
                ["Срок запуска", "2-3 месяца"],
                ["Окупаемость", "12-18 месяцев"],
                ["Рекомендуемый штат", "5-7 человек"]
            ]
            
            rec_table = Table(recommendations, colWidths=[doc.width*0.5, doc.width*0.5])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Arial-Bold'),
                ('FONTSIZE', (0, 0), (1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ]))
            elements.append(rec_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # Заключение
            elements.append(Paragraph("Заключение", self.styles['Heading2Custom']))
            elements.append(Paragraph(
                "Данный бизнес-план представляет собой базовый расчет затрат на открытие и развитие "
                f"бизнеса в сфере «{business_type}». Для более детального анализа "
                "рекомендуется обратиться к бизнес-консультанту или финансовому аналитику для "
                "учета специфики вашего региона и конкретных условий рынка.",
                self.styles['BodyTextCustom']
            ))
            
            # Финальный контакт
            elements.append(Spacer(1, 1*cm))
            elements.append(Paragraph(
                "Бизнес Конструктор - ваш надежный партнер в создании успешного бизнеса.",
                self.styles['BodyTextCustom']
            ))
            elements.append(Paragraph(
                "Контактный email: info@business-constructor.ru",
                self.styles['BodyTextCustom']
            ))
            
            # Собираем документ
            print("Сборка PDF документа...")
            doc.build(elements)
            
            # Возвращаем буфер с PDF данными
            buffer.seek(0)
            print("PDF документ успешно создан, размер:", len(buffer.getvalue()), "байт")
            return buffer
            
        except Exception as e:
            import traceback
            print(f"Ошибка при генерации PDF: {e}")
            print(traceback.format_exc())
            # Создаем простой PDF с сообщением об ошибке
            try:
                error_buffer = io.BytesIO()
                error_doc = SimpleDocTemplate(error_buffer, pagesize=A4)
                error_elements = []
                # Важно использовать встроенные стили, т.к. они точно есть
                error_elements.append(Paragraph("Произошла ошибка при создании PDF", self.styles['Heading1']))
                error_elements.append(Spacer(1, 1*cm))
                error_elements.append(Paragraph(f"Ошибка: {str(e)}", self.styles['Normal']))
                error_doc.build(error_elements)
                error_buffer.seek(0)
                return error_buffer
            except Exception as inner_error:
                print(f"Не удалось создать даже PDF с ошибкой: {inner_error}")
                # Если даже создание PDF с ошибкой не удалось, возвращаем пустой буфер
                empty_buffer = io.BytesIO()
                empty_buffer.write(b"Error generating PDF")
                empty_buffer.seek(0)
                return empty_buffer

# Функция для создания PDF отчета
def generate_pdf(result_data, business_options):
    try:
        print("Запуск генерации PDF через функцию generate_pdf")
        generator = PDFGenerator()
        pdf_buffer = generator.generate_business_plan_pdf(result_data, business_options)
        if pdf_buffer and hasattr(pdf_buffer, 'getvalue'):
            return pdf_buffer
        else:
            print("Ошибка: буфер PDF пуст или не является объектом BytesIO")
            # Создаем пустой буфер с сообщением об ошибке
            error_buffer = io.BytesIO()
            error_buffer.write(b"Error: PDF buffer is empty or invalid")
            error_buffer.seek(0)
            return error_buffer
    except Exception as e:
        print(f"Критическая ошибка в функции generate_pdf: {e}")
        import traceback
        print(traceback.format_exc())
        
        # Возвращаем пустой буфер с сообщением об ошибке
        error_buffer = io.BytesIO()
        error_buffer.write(f"Critical error in PDF generation: {str(e)}".encode('utf-8'))
        error_buffer.seek(0)
        return error_buffer 