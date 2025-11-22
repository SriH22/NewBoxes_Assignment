from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class TheHinduScraper(BaseScraper):
    def __init__(self):
        super().__init__("The Hindu")
        self.url = "https://www.thehindu.com/"
    
    def parse(self):
        """Parse The Hindu homepage for today's news"""
        articles = []
        
        response = self.make_request(self.url)
        if not response:
            return articles
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        article_selectors = [
            'h3.title a',
            'h2.title a',  
            'div.story-card a',
            'a[href*="/news/"]',
            'a[href*="/article"]',
            '.story-block h2 a',
            '.element h4 a',
        ]
        
        seen_titles = set()
        
        for selector in article_selectors:
            links = soup.select(selector)
            for link in links[:30]:
                title = link.get_text().strip()
                href = link.get('href')
                
                if (title and len(title) > 15 and href and 
                    ('/news/' in href or '/article' in href)):
                    
                    # Make absolute URL
                    if href.startswith('/'):
                        href = 'https://www.thehindu.com' + href
                    elif not href.startswith('http'):
                        href = 'https://www.thehindu.com' + href
                    
                    if title not in seen_titles:
                        seen_titles.add(title)
                        articles.append(self.create_article_object(title, href))
        
        return articles[:15]