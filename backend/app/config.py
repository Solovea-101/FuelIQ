from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./fueliq.db"
    SECRET_KEY: str = "dev-secret-key-fueliq-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    FUEL_PRICE_KES: float = 180.0
    ML_MODEL_PATH: str = "ml/models/fuel_consumption_model.joblib"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
