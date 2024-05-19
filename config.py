import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение значений переменных окружения
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")

# Подключение к базе данных
connection_string: str = (
    f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
)
async_engine = create_engine(
    f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
)
print(connection_string)  # Вывод строки подключения для проверки
