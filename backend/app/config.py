import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./t24_leads.db")
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    
    # Application settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LEAD_EXPIRY_HOURS: int = int(os.getenv("LEAD_EXPIRY_HOURS", "48"))
    
    # Email settings
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@t24leads.se")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.example.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

settings = Settings()
