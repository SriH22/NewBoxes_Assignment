import requests
from bs4 import BeautifulSoup
from datetime import datetime

class BaseScraper:
    def __init__(self, source_name):
        self.source_name = source_name
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def make_request(self, url):
        """Make HTTP request with error handling"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def create_article_object(self, title, link, **kwargs):
        """Create standardized article object"""
        return {
            'title': title,
            'link': link,
            'published': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': self.source_name,
            'summary': '',
            'date': datetime.now().strftime('%Y-%m-%d'),
            **kwargs
        }