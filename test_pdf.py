import os
import sys
import json
from pdf_generator import PDFGenerator

def test_pdf_generator():
    print("Запуск теста PDF генератора с кириллицей")
    
    # Создаем тестовые данные
    result_data = {
        "business_type": "Интернет-магазин",
        "business_size": "Средний",
        "price": 250000,
        "features": ["Сайт с каталогом", "CRM система", "Система аналитики"],
        # Добавляем тестовые данные для разбивки расходов
        "cost_breakdown": {
            "Оборудование и техника": 80000,
            "Аренда помещения": 40000,
            "Персонал и зарплаты": 65000,
            "Маркетинг и реклама": 30000,
            "Прочие расходы": 35000
        }
    }
    
    business_options = {
        "business_types": [
            {"id": 1, "name": "Интернет-магазин", "base_price": 100000},
            {"id": 2, "name": "Кафе", "base_price": 150000},
            {"id": 3, "name": "Салон красоты", "base_price": 120000}
        ],
        "business_sizes": [
            {"id": 1, "name": "Малый", "multiplier": 0.8},
            {"id": 2, "name": "Средний", "multiplier": 1.0},
            {"id": 3, "name": "Крупный", "multiplier": 1.5}
        ],
        "features": [
            {"id": 1, "name": "Сайт с каталогом", "price": 50000},
            {"id": 2, "name": "CRM система", "price": 80000},
            {"id": 3, "name": "Система аналитики", "price": 60000},
            {"id": 4, "name": "Мобильное приложение", "price": 120000}
        ]
    }
    
    try:
        # Создаем экземпляр генератора PDF
        generator = PDFGenerator()
        
        # Выводим информацию о разбивке расходов
        print("Тестовые данные включают разбивку расходов:")
        for category, amount in result_data["cost_breakdown"].items():
            percentage = round((amount / result_data["price"]) * 100, 1)
            print(f"  - {category}: {amount} руб. ({percentage}%)")
        
        # Генерируем PDF
        print("Генерация PDF...")
        pdf_buffer = generator.generate_business_plan_pdf(result_data, business_options)
        
        # Сохраняем PDF в файл
        output_path = "test_business_plan.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"PDF файл успешно создан и сохранен в {output_path}")
        print(f"Размер файла: {os.path.getsize(output_path)} байт")
        print("Пожалуйста, проверьте файл на наличие всех секций, включая новый раздел с детализацией расходов")
        return True
    except Exception as e:
        print(f"Ошибка при тестировании PDF генератора: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_pdf_generator() 