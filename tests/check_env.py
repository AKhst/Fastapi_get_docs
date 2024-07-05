# check_env.py
import os
from dotenv import load_dotenv

# Загрузите переменные окружения
load_dotenv("/Users/admin/PycharmProjects/Fastapi_get_docs/.test.env")

# Получите переменные окружения
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")
celery_broker_url = os.getenv("CELERY_BROKER_URL")
celery_result_backend = os.getenv("CELERY_RESULT_BACKEND")
tessdata_prefix = os.getenv("TESSDATA_PREFIX")

# Выведите переменные окружения для отладки
print("DB_HOST:", db_host)
print("DB_PORT:", db_port)
print("DB_USER:", db_user)
print("DB_PASS:", db_pass)
print("DB_NAME:", db_name)
print("CELERY_BROKER_URL:", celery_broker_url)
print("CELERY_RESULT_BACKEND:", celery_result_backend)
print("TESSDATA_PREFIX:", tessdata_prefix)
# Создание SQLAlchemy async_engine для операций с базой данных
