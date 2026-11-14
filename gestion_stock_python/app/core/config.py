import os

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ["DB_URL"]
DB_POOL = int(os.getenv("DB_POOL", "10"))