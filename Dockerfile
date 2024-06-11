FROM python:3.12-slim

RUN mkdir /app
# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

COPY . .
# Устанавливаем зависимости
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Устанавливаем Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-rus

# Устанавливаем переменную окружения TESSDATA_PREFIX
ENV TESSDATA_PREFIX /usr/share/tesseract-ocr/4.00/tessdata/

# Устанавливаем путь к Alembic в переменную PATH
ENV PATH="${PATH}:/app/alembic"

# Выполняем миграции перед запуском приложения
RUN poetry run alembic upgrade head

# Открываем порт для приложения
EXPOSE 8000

# Команда по умолчанию для запуска FastAPI приложения
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
