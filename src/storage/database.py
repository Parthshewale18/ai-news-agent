"""
Database models and setup
Using SQLAlchemy ORM with SQLite
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from typing import List
from config.settings import settings

Base = declarative_base()


class Article(Base):
    """News article model"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    source_name = Column(String(200), nullable=False)
    source_domain = Column(String(200), nullable=False)
    published_at = Column(DateTime, nullable=False)
    content = Column(Text)
    summary = Column(Text)
    
    # Analysis results
    is_ai_relevant = Column(Boolean, default=False)
    ai_confidence = Column(Float, default=0.0)
    credibility_score = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)
    verification_reason = Column(Text)
    
    # Notification status
    notification_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...', source='{self.source_name}')>"


class Subscriber(Base):
    """Telegram subscriber model"""
    __tablename__ = "subscribers"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String(100), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Subscription status
    is_active = Column(Boolean, default=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    unsubscribed_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Subscriber(chat_id='{self.chat_id}', username='{self.username}', active={self.is_active})>"


class NotificationLog(Base):
    """Log of sent notifications"""
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, nullable=False, index=True)
    chat_id = Column(String(100), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<NotificationLog(article_id={self.article_id}, chat_id='{self.chat_id}', success={self.success})>"


# Database engine and session
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug_mode
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session (for dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_recent_articles(db, hours: int = 24) -> List[Article]:
    """Get AI-relevant articles from the last N hours"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    return db.query(Article).filter(
        Article.published_at >= cutoff_time,
        Article.is_ai_relevant == True,
        Article.is_verified == True
    ).order_by(Article.published_at.desc()).all()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")


if __name__ == "__main__":
    init_db()
