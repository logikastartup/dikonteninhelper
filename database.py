import os
import configparser
import sqlite3
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Create data directory if it doesn't exist
data_folder = config.get('storage', 'save_folder', fallback='data')
os.makedirs(data_folder, exist_ok=True)

# Database setup
database_path = config.get('storage', 'database_path', fallback='data/crawled_data.db')
engine = create_engine(f'sqlite:///{database_path}')
Base = declarative_base()
Session = sessionmaker(bind=engine)


class CrawledPage(Base):
    """Model for storing crawled web pages"""
    __tablename__ = 'crawled_pages'

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(String)
    content = Column(Text)
    html = Column(Text)
    last_crawled_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "last_crawled_at": self.last_crawled_at.isoformat()
        }


def init_db():
    """Initialize database and tables"""
    Base.metadata.create_all(engine)


def get_session():
    """Get database session"""
    return Session()


def save_crawled_page(url, title, description, content, html):
    """Save crawled page to database"""
    session = get_session()
    try:
        # Check if page already exists
        existing = session.query(CrawledPage).filter_by(url=url).first()
        
        if existing:
            # Update existing record
            existing.title = title
            existing.description = description
            existing.content = content
            existing.html = html
            existing.last_crawled_at = datetime.now()
        else:
            # Create new record
            page = CrawledPage(
                url=url,
                title=title,
                description=description,
                content=content,
                html=html
            )
            session.add(page)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_crawled_page(url):
    """Get crawled page from database"""
    session = get_session()
    try:
        page = session.query(CrawledPage).filter_by(url=url).first()
        return page.to_dict() if page else None
    finally:
        session.close()


def should_recrawl(url, skip_days=None):
    """Check if page should be recrawled based on last crawl date"""
    if skip_days is None:
        config = configparser.ConfigParser()
        config.read('config.ini')
        skip_days = config.getint('crawler', 'skip_crawl_time', fallback=60)
    
    session = get_session()
    try:
        page = session.query(CrawledPage).filter_by(url=url).first()
        if not page:
            return True
        
        # Check if page was crawled more than skip_days ago
        now = datetime.now()
        delta = now - page.last_crawled_at
        return delta.days >= skip_days
    finally:
        session.close()
