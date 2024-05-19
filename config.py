import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment variables from the .env file
load_dotenv()

# Get environment variable values
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")

# Create connection string for asynchronous connection
connection_string = (
    f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
)

# Create asynchronous engine
async_engine = create_async_engine(connection_string, echo=True)

# Print connection string for verification
print(connection_string)
