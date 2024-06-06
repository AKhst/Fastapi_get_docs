# Используйте официальный образ Python в качестве базового образа
FROM python:3.12-slim

# Установите необходимые системные зависимости
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    wget \
    && apt-get clean

# Установите Poetry
RUN pip install poetry

# Создайте рабочую директорию
WORKDIR /app

# Скопируйте файлы pyproject.toml и poetry.lock (если он есть)
COPY pyproject.toml poetry.lock* /app/

# Установите зависимости проекта
RUN poetry install --no-root

# Скопируйте оставшийся исходный код проекта
COPY . /app

# Экспортируйте переменную окружения для Tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

# Команда для запуска приложения
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
