from newspaper import Article
import time
from datetime import datetime
from utils.selenium_helper import SeleniumHelper
from services.groq_service import GroqService
from config.settings import Settings

class ArticleProcessor:
    def __init__(self, groq_service=None):
        self.groq_service = groq_service
        self.selenium_helper = SeleniumHelper()
    
    def extract_article_content(self, url):
        """Extract article content using newspaper3k"""
        try:
            print(f"   Downloading article content...")
            article = Article(url)
            article.download()
            article.parse()
            
            content_data = {
                'title': article.title,
                'authors': article.authors,
                'publish_date': str(article.publish_date) if article.publish_date else None,
                'text': article.text,
                'top_image': article.top_image,
                'summary': article.summary,
                'content_length': len(article.text)
            }
            print(f"   ✅ Content extracted ({len(article.text)} characters)")
            return content_data
            
        except Exception as e:
            print(f"   ❌ Error extracting content: {str(e)[:100]}...")
            return None
    
    def process_single_article(self, article, index, total):
        """Process a single article with comprehensive error handling"""
        print(f"\n🔍 Processing {index}/{total}: {article['title'][:60]}...")
        
        final_url = article['link']
        article_content = None
        needs_selenium = False
        
        try:
            # First try to extract content directly
            print("   Trying direct content extraction...")
            article_content = self.extract_article_content(final_url)
            
            # If direct extraction fails, try with Selenium
            if not article_content or len(article_content.get('text', '')) < 100:
                print("   Direct extraction failed, trying with Selenium...")
                needs_selenium = True
                final_url = self.selenium_helper.get_final_url_selenium(final_url)
                article_content = self.extract_article_content(final_url)
            
            # Get summary and keywords using Groq API if available
            groq_data = {"summary": "", "keywords": []}
            if article_content and article_content.get('text') and self.groq_service:
                print("   Generating summary and keywords with Groq...")
                groq_data = self.groq_service.summarize_article(
                    article_content.get('text', ''), 
                    article_content.get('title', article['title'])
                )
            
        except Exception as e:
            print(f"   ❌ Unexpected error processing article: {str(e)[:100]}...")
        
        # Create final article object
        final_article = {
            'title': article['title'],
            'source': article['source'],
            'link': article['link'],
            'final_url': final_url,
            'date': article['date'],
            'published_date': article['published'],
            'processed_at': datetime.now().isoformat(),
            'used_selenium': needs_selenium,
            'success': article_content is not None and article_content.get('text', '')
        }
        
        # Add extracted content if available
        if article_content:
            final_article.update(article_content)
        else:
            # Add placeholder for failed extraction
            final_article.update({
                'title': article['title'],
                'authors': [],
                'publish_date': None,
                'text': '',
                'top_image': '',
                'summary': '',
                'content_length': 0
            })
        
        # Add Groq-generated data
        final_article.update({
            'ai_summary': groq_data['summary'],
            'keywords': groq_data['keywords']
        })
        
        return final_article