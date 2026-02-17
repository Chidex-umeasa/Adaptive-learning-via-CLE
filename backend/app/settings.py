from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./adaptive_load.db"
    APP_NAME: str = "Adaptive Load Tutor API"
    SECRET_KEY: str = "dev-secret-change-me"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"

settings = Settings()
