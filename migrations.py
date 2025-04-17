import psycopg2
from config import DATABASE_URI

def migrate_messages_table():
    """
    Добавляет поля response и response_sent_at в таблицу messages.
    """
    # Извлекаем параметры подключения из URI
    uri = DATABASE_URI.replace('postgresql://', '')
    user_pass, host_db = uri.split('@')
    user, password = user_pass.split(':')
    host, database = host_db.split('/')
    host, port = host.split(':')
    
    # Подключаемся к базе данных
    conn = psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )
    
    # Создаем курсор
    cursor = conn.cursor()
    
    try:
        # Проверяем, существуют ли уже столбцы
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'messages' 
              AND column_name IN ('response', 'response_sent_at');
        """)
        
        existing_columns = [col[0] for col in cursor.fetchall()]
        
        # Добавляем столбцы, если они не существуют
        if 'response' not in existing_columns:
            print("Добавление столбца 'response' в таблицу messages...")
            cursor.execute("""
                ALTER TABLE messages
                ADD COLUMN response TEXT;
            """)
        
        if 'response_sent_at' not in existing_columns:
            print("Добавление столбца 'response_sent_at' в таблицу messages...")
            cursor.execute("""
                ALTER TABLE messages
                ADD COLUMN response_sent_at TIMESTAMP;
            """)
        
        # Подтверждаем изменения
        conn.commit()
        print("Миграция успешно выполнена.")
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при выполнении миграции: {e}")
    
    finally:
        # Закрываем соединение
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate_messages_table() 