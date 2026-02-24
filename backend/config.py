from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://wellsync:wellsync123@localhost:5432/wellsync"
    secret_key: str = "dev-secret-change-in-prod"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    ml_models_dir: str = "./ml_models"
    anthropic_api_key: str = ""
    agent_loop_interval_hours: int = 1

    class Config:
        env_file = ".env"


settings = Settings()
