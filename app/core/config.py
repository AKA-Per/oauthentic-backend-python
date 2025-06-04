from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str # Refer to the DATABASE_URL in environment variable
    sync_db_uri: str
    access_token_expiry: int = 3000
    token_secret_key: str
    token_algorithm: str = "HS256"
    
    class Config:
        env_file = ".env"
        
    


settings = Settings()