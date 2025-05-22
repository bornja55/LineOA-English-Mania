# app/core/config.py
import os
from pydantic_settings import BaseSettings
from functools import lru_cache

# Debug prints
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
#print("DEBUG: ENV PATH =", env_path)
#print("DEBUG: FILE EXISTS =", os.path.exists(env_path))
#if os.path.exists(env_path):
#    with open(env_path) as f:
#        print("DEBUG: ENV CONTENTS\n", f.read())
#else:
#    print("DEBUG: .env file not found at", env_path)

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    DATABASE_URL: str
    LINE_LOGIN_CHANNEL_ID: str
    LINE_LOGIN_CHANNEL_SECRET: str
    LINE_MESSAGING_CHANNEL_ID: str
    LINE_MESSAGING_CHANNEL_SECRET: str
    LINE_CHANNEL_ACCESS_TOKEN: str
    
    class Config:
        env_file = env_path

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

# More debug prints
#print("DEBUG: SETTINGS SECRET_KEY =", settings.SECRET_KEY)
#print("DEBUG: SETTINGS ALGORITHM =", settings.ALGORITHM)
#print("DEBUG: SETTINGS DATABASE_URL =", settings.DATABASE_URL)
