import requests
import json

def test_calculate_api():
    print("Тестирование API расчета цены...")
    
    # Создаем тестовые данные
    test_data = {
        "business_type": "retail",
        "business_size": "small",
        "features": ["website", "crm"]
    }
    
    try:
        # Отправляем запрос к API
        response = requests.post(
            "http://127.0.0.1:5000/calculate", 
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Выводим статус ответа
        print(f"Статус ответа: {response.status_code}")
        
        # Выводим содержимое ответа
        print(f"Содержимое ответа: {response.text}")
        
        # Если ответ успешный, проверяем рассчитанную цену
        if response.status_code == 200:
            result = response.json()
            print(f"Рассчитанная цена: {result.get('price')} руб.")
            return True
        else:
            print(f"Ошибка: {response.text}")
            return False
            
    except Exception as e:
        print(f"Произошла ошибка при тестировании: {e}")
        return False

if __name__ == "__main__":
    # Запускаем тест
    success = test_calculate_api()
    
    if success:
        print("Тест успешно выполнен!")
    else:
        print("Тест не пройден!") 