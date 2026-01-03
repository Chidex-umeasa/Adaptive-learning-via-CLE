from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./adaptive_load.db"
    APP_NAME: str = "Adaptive Load Tutor API"

    class Config:
        env_file = ".env"

settings = Settings()
