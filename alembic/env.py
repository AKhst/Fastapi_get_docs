import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Импортируем модели и конфигурацию базы данных
from myapp import models
from myapp.config import DATABASE_URL

# Подключаем файл конфигурации логирования
config = context.config
fileConfig(config.config_file_name)

# Создаем асинхронный event loop
loop = asyncio.get_event_loop()

# Настраиваем подключение к базе данных
config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = models.Base.metadata

# Определяем асинхронный engine для работы с базой данных
async_engine = engine_from_config(
    config.get_section(config.config_ini_section),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
    future=True,  # Включаем использование асинхронного интерфейса SQLAlchemy
    loop=loop,
)


# Определяем асинхронную функцию для выполнения миграций
async def run_migrations():
    async with async_engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        async with connection.begin():
            await context.run_migrations()


# Определяем асинхронные функции для выполнения миграций
async def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        await context.run_migrations()


async def run_migrations_online():
    connectable = async_engine

    async with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        async with connection.begin():
            await context.run_migrations()


# Выполняем миграции
if context.is_offline_mode():
    loop.run_until_complete(run_migrations_offline())
else:
    loop.run_until_complete(run_migrations_online())
