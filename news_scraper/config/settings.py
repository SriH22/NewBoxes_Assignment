import os
from datetime import datetime

class Settings:
    # API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    
    # File Settings
    JSON_OUTPUT_DIR = "output"
    
    # Scraping Settings
    REQUEST_TIMEOUT = 10
    SELENIUM_TIMEOUT = 30
    DELAY_BETWEEN_REQUESTS = 2
    
    # Content Settings
    MAX_CONTENT_LENGTH = 8000
    SIMILARITY_THRESHOLD = 0.7
    
    @classmethod
    def get_json_filename(cls):
        current_date = datetime.now().strftime('%Y-%m-%d')
        return f"news_articles_{current_date}.json"
    
    @classmethod
    def get_full_json_path(cls):
        filename = cls.get_json_filename()
        return f"{cls.JSON_OUTPUT_DIR}/{filename}" if cls.JSON_OUTPUT_DIR else filename