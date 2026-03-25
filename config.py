import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    phone_number: str = os.getenv("PHONE_NUMBER")
    bot_token: str = os.getenv("BOT_TOKEN")
    api_id: int = int(os.getenv("API_ID"))
    api_hash: str = os.getenv("API_HASH")
    session_name: str = os.getenv("SESSION_NAME")
    db_url: str = os.getenv("DB_URL")
    ai_api_key: str = os.getenv("AI_API_KEY")

config_p = Config()