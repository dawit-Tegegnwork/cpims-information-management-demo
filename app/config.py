from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CPIMS Information Management Demo"
    database_url: str = "sqlite:///./cpims_demo.db"
    debug: bool = False

    class Config:
        env_file = ".env"
        env_prefix = "CPIMS_"


settings = Settings()
