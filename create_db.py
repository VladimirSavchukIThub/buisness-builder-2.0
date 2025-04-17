import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to PostgreSQL server
conn = psycopg2.connect(
    user="postgres",
    password="postgres",
    host="localhost",
    port="5433"
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Create a cursor
cursor = conn.cursor()

# Create the database
try:
    cursor.execute("CREATE DATABASE business_constructor")
    print("Database 'business_constructor' created successfully")
except psycopg2.errors.DuplicateDatabase:
    print("Database 'business_constructor' already exists")
except Exception as e:
    print(f"Error creating database: {e}")

# Close the cursor and connection
cursor.close()
conn.close() 