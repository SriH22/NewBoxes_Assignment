from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class TimesOfIndiaScraper(BaseScraper):
    def __init__(self):
        super().__init__("Times of India")
        self.url = "https://timesofindia.indiatimes.com/"
    
    def parse(self):
        """Parse Times of India homepage for today's news"""
        articles = []
        
        response = self.make_request(self.url)
        if not response:
            return articles
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        article_selectors = [
            'div.w_tle a',
            'div.top-story a',
            'a[href*="/articleshow/"]',
            '.headline a',
            '.title a'
        ]
        
        seen_titles = set()
        
        for selector in article_selectors:
            links = soup.select(selector)
            for link in links[:25]:
                title = link.get_text().strip()
                href = link.get('href')
                
                if title and len(title) > 15 and href and '/articleshow/' in href:
                    if href.startswith('/'):
                        href = 'https://timesofindia.indiatimes.com' + href
                    
                    if title not in seen_titles:
                        seen_titles.add(title)
                        articles.append(self.create_article_object(title, href))
        
        return articles[:15]