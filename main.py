import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify .env values (optional, for debugging)
print("Connecting to database:")
print("HOST:", os.getenv("DB_HOST"))
print("PORT:", os.getenv("DB_PORT"))
print("USER:", os.getenv("DB_USER"))
print("DB:", os.getenv("DB_NAME"))

timeout = 10

# ✅ Correct pymysql.connect parameters
connection = pymysql.connect( # type: ignore
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"), # type: ignore
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT")), # type: ignore
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
    connect_timeout=timeout,
    read_timeout=timeout,
    write_timeout=timeout,
    ssl={"ssl": {}}  # ✅ required for Aiven (Pylance might still warn, but it works)
)

try:
    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS mytest (id INTEGER PRIMARY KEY AUTO_INCREMENT)")
        cursor.execute("INSERT INTO mytest (id) VALUES (1), (2)")
        cursor.execute("SELECT * FROM mytest")
        print(cursor.fetchall())
finally:
    connection.close()
