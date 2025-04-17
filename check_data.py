import psycopg2

# Подключение к базе данных
conn = psycopg2.connect(
    user="postgres",
    password="postgres",
    host="localhost",
    port="5433",
    database="business_constructor"
)

cursor = conn.cursor()

# Проверка наличия данных в таблицах
tables = ['business_types', 'business_sizes', 'features', 'examples', 'articles', 'users', 'messages']

print("Проверка количества записей в таблицах:")
for table in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Таблица {table}: {count} записей")
        
        # Если таблица пуста, выводим подробности
        if count == 0:
            print(f"  Таблица {table} пуста!")
        # Если в таблице есть записи, выводим первые 3
        else:
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            rows = cursor.fetchall()
            print(f"  Примеры данных: {rows}")
            
    except Exception as e:
        print(f"Ошибка при проверке таблицы {table}: {e}")

# Закрытие соединения
cursor.close()
conn.close() 