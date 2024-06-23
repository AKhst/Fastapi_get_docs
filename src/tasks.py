import os
import logging
import asyncio
from dotenv import load_dotenv
from celery import Celery
import pytesseract

from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from src.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, connection_string
from src.models import DocumentsText

# Загрузить переменные окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Установить переменную окружения TESSDATA_PREFIX
tessdata_prefix = os.getenv("TESSDATA_PREFIX")

if tessdata_prefix:
    os.environ["TESSDATA_PREFIX"] = tessdata_prefix
    logger.info(f"TESSDATA_PREFIX set to: {tessdata_prefix}")

# Создаем экземпляр Celery
celery = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
celery.conf.broker_connection_retry_on_startup = True

# Настраиваем асинхронный движок и сессии SQLAlchemy
async_engine = create_async_engine(connection_string, future=True, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def extract_text(file_path, image_id):
    img = Image.open(file_path)

    # Вывод значения переменной окружения для отладки
    logger.info(f"TESSDATA_PREFIX (inside task): {os.getenv('TESSDATA_PREFIX')}")

    text = pytesseract.image_to_string(img, lang="rus")

    async with AsyncSessionLocal() as session:
        try:
            text_p = DocumentsText(id_doc=image_id, text=text)
            session.add(text_p)
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Failed to save text to database: {e}")
            raise e
        finally:
            await session.close()

    return text


@celery.task(name="src.tasks.extract_text_from_image")
def extract_text_from_image(file_path, image_id):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(extract_text(file_path, image_id))


# Вывести значение переменной окружения TESSDATA_PREFIX
print("TESSDATA_PREFIX:", tessdata_prefix)
