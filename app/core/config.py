from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    ollama_url: str = "http://localhost:11434/api/generate"
    ollama_model: str = "llama3"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    rss_feeds: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
