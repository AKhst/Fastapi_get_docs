from dotenv import dotenv_values
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment variables from the .env file
config = dotenv_values("/Users/admin/PycharmProjects/Fastapi_get_docs/.env")

# Get environment variable values
db_host = config.get("DB_HOST")
db_port = config.get("DB_PORT")
db_user = config.get("DB_USER")
db_pass = config.get("DB_PASS")
db_name = config.get("DB_NAME")

# Print the loaded environment variables for debugging
print("Loaded environment variables:")
print("DB_HOST:", db_host)
print("DB_PORT:", db_port)
print("DB_USER:", db_user)
print("DB_PASS:", db_pass)
print("DB_NAME:", db_name)

# Check if all required environment variables are set
if not all([db_host, db_port, db_user, db_pass, db_name]):
    raise ValueError("One or more required environment variables are not set.")

# Create connection string for asynchronous connection
connection_string = (
    f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
)
CELERY_BROKER_URL = config.get("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = config.get("CELERY_RESULT_BACKEND")

# Create asynchronous engine
async_engine = create_async_engine(connection_string, echo=True)

print(
    f"{db_user}, {db_pass}, {db_host}, {db_port}, {db_name}, {CELERY_BROKER_URL},{CELERY_RESULT_BACKEND}"
)
