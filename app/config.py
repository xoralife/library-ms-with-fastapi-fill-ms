from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
import os


class Settings(BaseSettings):
    app_name: str = "Library Management System"
    app_version: str = "1.0.0"
    debug: bool = True

    db_type: str = "sqlite"
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "library_ms"
    db_echo: bool = False

    jwt_secret_key: str = "change-this-to-a-random-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    admin_email: str = "admin@library.com"
    admin_username: str = "admin"
    admin_password: str = "Admin@123"

    upload_dir: str = "uploads"
    max_upload_size: int = 5_242_880  # 5MB

    @property
    def database_url(self) -> str:
        if self.db_type == "sqlite":
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"{self.db_name}.db")
            return f"sqlite+aiosqlite:///{db_path}"
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def database_url_sync(self) -> str:
        if self.db_type == "sqlite":
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"{self.db_name}.db")
            return f"sqlite:///{db_path}"
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
