from pydantic import Field
from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    """Redis configuration settings"""
    
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_PASSWORD: str = Field(default="", description="Redis password")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    REDIS_URL: str = Field(default="", description="Redis URL (overrides other settings if provided)")
    SME_SESSION_TTL: int = Field(default=3600, description="Session TTL in seconds")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


redis_settings = RedisSettings()
