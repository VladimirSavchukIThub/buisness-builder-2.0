import requests
import json
import os
import time
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('bank_api')

# Путь для кэширования данных
CACHE_FILE = "bank_rates_cache.json"
# Время жизни кэша в секундах (по умолчанию 24 часа)
CACHE_TTL = 86400

class BankAPI:
    """Класс для работы с банковскими API и получения актуальных кредитных ставок"""
    
    def __init__(self):
        self.banks = [
            {
                "name": "Сбербанк",
                "logo": "sberbank_logo.png",
                "business_loans": {
                    "url": "https://api.example.com/sberbank/business_loans",
                    "api_key": os.environ.get("SBERBANK_API_KEY", ""),
                    "min_rate": 9.5,
                    "max_rate": 15.8,
                    "loan_term": "до 5 лет"
                }
            },
            {
                "name": "ВТБ",
                "logo": "vtb_logo.png",
                "business_loans": {
                    "url": "https://api.example.com/vtb/business_loans",
                    "api_key": os.environ.get("VTB_API_KEY", ""),
                    "min_rate": 10.2,
                    "max_rate": 16.5,
                    "loan_term": "до 7 лет"
                }
            },
            {
                "name": "Альфа-Банк",
                "logo": "alfabank_logo.png",
                "business_loans": {
                    "url": "https://api.example.com/alfabank/business_loans",
                    "api_key": os.environ.get("ALFABANK_API_KEY", ""),
                    "min_rate": 9.9,
                    "max_rate": 17.3,
                    "loan_term": "до 3 лет"
                }
            },
            {
                "name": "Тинькофф Бизнес",
                "logo": "tinkoff_logo.png",
                "business_loans": {
                    "url": "https://api.example.com/tinkoff/business_loans",
                    "api_key": os.environ.get("TINKOFF_API_KEY", ""),
                    "min_rate": 11.0,
                    "max_rate": 18.0,
                    "loan_term": "до 3 лет"
                }
            },
            {
                "name": "Открытие",
                "logo": "open_logo.png",
                "business_loans": {
                    "url": "https://api.example.com/open/business_loans",
                    "api_key": os.environ.get("OPEN_API_KEY", ""),
                    "min_rate": 10.5,
                    "max_rate": 16.8,
                    "loan_term": "до 5 лет"
                }
            }
        ]
    
    def _load_cache(self):
        """Загружает кэшированные данные о ставках"""
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                # Проверяем, не устарел ли кэш
                cache_time = cache_data.get('timestamp', 0)
                if time.time() - cache_time <= CACHE_TTL:
                    logger.info(f"Загружены кэшированные данные от {datetime.fromtimestamp(cache_time)}")
                    return cache_data.get('rates', [])
            
            return None
        except Exception as e:
            logger.error(f"Ошибка при загрузке кэша: {e}")
            return None
    
    def _save_cache(self, rates_data):
        """Сохраняет данные о ставках в кэш"""
        try:
            cache_data = {
                'timestamp': time.time(),
                'rates': rates_data
            }
            
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=4)
            
            logger.info("Данные успешно сохранены в кэш")
        except Exception as e:
            logger.error(f"Ошибка при сохранении кэша: {e}")
    
    def fetch_rate_from_api(self, bank):
        """Запрашивает актуальные ставки из API конкретного банка"""
        try:
            # В реальном приложении здесь был бы настоящий API-запрос
            # Для демонстрации используем предустановленные значения
            logger.info(f"Запрос ставок из API банка {bank['name']}")
            
            # Имитация запроса к API
            # В реальном приложении:
            # response = requests.get(
            #     bank['business_loans']['url'],
            #     headers={'Authorization': f"Bearer {bank['business_loans']['api_key']}"}
            # )
            # if response.status_code == 200:
            #     data = response.json()
            #     return {
            #         'min_rate': data['min_interest_rate'],
            #         'max_rate': data['max_interest_rate'],
            #         'loan_term': data['loan_term']
            #     }
            
            # Используем заготовленные данные для демонстрации
            return {
                'min_rate': bank['business_loans']['min_rate'],
                'max_rate': bank['business_loans']['max_rate'],
                'loan_term': bank['business_loans']['loan_term']
            }
            
        except Exception as e:
            logger.error(f"Ошибка при запросе к API банка {bank['name']}: {e}")
            # В случае ошибки возвращаем стандартные значения
            return {
                'min_rate': bank['business_loans']['min_rate'],
                'max_rate': bank['business_loans']['max_rate'],
                'loan_term': bank['business_loans']['loan_term']
            }
    
    def get_rates(self, force_refresh=False):
        """Получает актуальные кредитные ставки всех банков"""
        # Пробуем загрузить данные из кэша, если не требуется принудительное обновление
        if not force_refresh:
            cached_rates = self._load_cache()
            if cached_rates:
                return cached_rates
        
        rates_data = []
        
        # Запрашиваем данные у каждого банка
        for bank in self.banks:
            bank_data = {
                'name': bank['name'],
                'logo': bank['logo']
            }
            
            # Получаем актуальные ставки
            loan_rates = self.fetch_rate_from_api(bank)
            bank_data.update(loan_rates)
            
            rates_data.append(bank_data)
        
        # Сохраняем полученные данные в кэш
        self._save_cache(rates_data)
        
        return rates_data
    
    def get_average_rate(self):
        """Возвращает среднюю ставку по всем банкам"""
        rates = self.get_rates()
        
        if not rates:
            return 0
        
        min_rates = [rate['min_rate'] for rate in rates]
        max_rates = [rate['max_rate'] for rate in rates]
        
        avg_min_rate = sum(min_rates) / len(min_rates)
        avg_max_rate = sum(max_rates) / len(max_rates)
        
        return {
            'avg_min_rate': round(avg_min_rate, 2),
            'avg_max_rate': round(avg_max_rate, 2)
        }
    
    def get_best_rate(self):
        """Возвращает информацию о банке с лучшей (минимальной) ставкой"""
        rates = self.get_rates()
        
        if not rates:
            return None
        
        best_rate = min(rates, key=lambda x: x['min_rate'])
        return best_rate
    
    def calculate_loan_payments(self, loan_amount, interest_rate, loan_term_years):
        """
        Расчет ежемесячного платежа по кредиту
        
        Args:
            loan_amount: сумма кредита
            interest_rate: годовая процентная ставка (в процентах)
            loan_term_years: срок кредита в годах
            
        Returns:
            dict: словарь с информацией о платеже
        """
        # Преобразуем годовую ставку в месячную (в десятичном виде)
        monthly_rate = interest_rate / 100 / 12
        
        # Общее количество платежей
        total_payments = loan_term_years * 12
        
        # Расчет ежемесячного платежа по формуле аннуитетного платежа
        if monthly_rate == 0:
            monthly_payment = loan_amount / total_payments
        else:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** total_payments) / ((1 + monthly_rate) ** total_payments - 1)
        
        # Общая сумма выплат
        total_payment = monthly_payment * total_payments
        
        # Общая сумма переплаты
        total_interest = total_payment - loan_amount
        
        return {
            'monthly_payment': round(monthly_payment, 2),
            'total_payment': round(total_payment, 2),
            'total_interest': round(total_interest, 2),
            'total_payments': total_payments
        }


# Функция для получения кредитных ставок
def get_business_loan_rates(force_refresh=False):
    """Получает актуальные кредитные ставки для бизнес-кредитов"""
    api = BankAPI()
    return api.get_rates(force_refresh)

# Функция для расчета платежей по кредиту
def calculate_business_loan(loan_amount, interest_rate, loan_term_years):
    """Расчет параметров бизнес-кредита"""
    api = BankAPI()
    return api.calculate_loan_payments(loan_amount, interest_rate, loan_term_years)

# Если файл запущен напрямую, выполняем тестовый запрос
if __name__ == "__main__":
    print("Тестирование API банков...")
    api = BankAPI()
    rates = api.get_rates(force_refresh=True)
    
    print(f"Получены ставки от {len(rates)} банков:")
    for rate in rates:
        print(f"{rate['name']}: {rate['min_rate']}% - {rate['max_rate']}% ({rate['loan_term']})")
    
    average = api.get_average_rate()
    print(f"\nСредняя ставка по рынку: {average['avg_min_rate']}% - {average['avg_max_rate']}%")
    
    best = api.get_best_rate()
    print(f"Лучшее предложение: {best['name']} - {best['min_rate']}%")
    
    # Тестовый расчет кредита
    loan_amount = 1000000
    interest_rate = 12
    loan_term_years = 3
    
    payment_info = api.calculate_loan_payments(loan_amount, interest_rate, loan_term_years)
    print(f"\nРасчет кредита на сумму {loan_amount} руб. под {interest_rate}% на {loan_term_years} лет:")
    print(f"Ежемесячный платеж: {payment_info['monthly_payment']} руб.")
    print(f"Общая сумма выплат: {payment_info['total_payment']} руб.")
    print(f"Сумма переплаты: {payment_info['total_interest']} руб.") 