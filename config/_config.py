from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_default_region: str

    class Config:
        env_file = ".env"


settings = Settings()
