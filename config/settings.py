"""
Application configuration management
Loads settings from environment variables
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Required API Keys
    gemini_api_key: str
    telegram_bot_token: str
    telegram_webhook_url: str
    
    # Database
    database_url: str = "sqlite:///ainews.db"
    
    # Optional APIs
    newsapi_key: Optional[str] = None
    
    # Configuration
    polling_interval: int = 1800  # 30 minutes
    verification_threshold: int = 70
    max_subscribers: int = 100000
    ai_relevance_threshold: int = 85
    max_articles_per_cycle: int = 500
    debug_mode: bool = False
    
    # Optional WhatsApp (premium tier)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_number: Optional[str] = None
    
    # Optional Payment
    razorpay_key_id: Optional[str] = None
    razorpay_key_secret: Optional[str] = None
    premium_price: int = 900  # ₹9 in paise
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
