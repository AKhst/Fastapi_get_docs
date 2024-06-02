from celery import Celery
import pytesseract
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from src.config import connection_string, CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from src.models import DocumentsText
import logging
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем экземпляр Celery
celery = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
celery.conf.broker_connection_retry_on_startup = True

# Настраиваем асинхронный движок и сессии SQLAlchemy
async_engine = create_async_engine(connection_string, future=True, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


@celery.task(name="src.tasks.extract_text_from_image")
def extract_text_from_image(file_path, image_id):
    async def async_task():
        img = Image.open(file_path)
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

    # Запуск асинхронного кода
    return asyncio.run(async_task())
