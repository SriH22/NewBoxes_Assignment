import time
from config.settings import Settings
from scraper.the_hindu_scraper import TheHinduScraper
from scraper.times_of_india_scraper import TimesOfIndiaScraper
from scraper.article_processor import ArticleProcessor
from services.groq_service import GroqService
from utils.file_handler import FileHandler
from utils.duplicate_checker import DuplicateChecker

class NewsScraper:
    def __init__(self, groq_api_key=None):
        self.groq_service = GroqService(groq_api_key) if groq_api_key else None
        self.article_processor = ArticleProcessor(self.groq_service)
        self.file_handler = FileHandler()
        self.duplicate_checker = DuplicateChecker()
        
        # Initialize scrapers
        self.scrapers = [
            TheHinduScraper(),
            TimesOfIndiaScraper()
        ]
    
    def scrape_news(self):
        """Main function to scrape news from all sources"""
        print("🚀 Starting News Scraping...")
        
        # Get filename for current date
        filename = Settings.get_full_json_path()
        print(f"📁 Target file: {filename}")
        
        # Load existing articles
        existing_articles = self.file_handler.load_existing_articles(filename)
        print(f"📊 Found {len(existing_articles)} existing articles in {filename}")
        
        # Scrape from all sources
        all_scraped_articles = []
        for scraper in self.scrapers:
            print(f"📰 Fetching {scraper.source_name}...")
            articles = scraper.parse()
            print(f"✅ Found {len(articles)} {scraper.source_name} articles")
            all_scraped_articles.extend(articles)
        
        print(f"📊 Total articles scraped: {len(all_scraped_articles)}")
        
        # Filter out duplicates
        new_articles_to_process = self.duplicate_checker.filter_new_articles(
            all_scraped_articles, existing_articles
        )
        
        if not new_articles_to_process:
            print("🎉 No new articles to process! All articles are already in the database.")
            return existing_articles
        
        print(f"🆕 Processing {len(new_articles_to_process)} new articles...")
        
        processed_articles = []
        successful_articles = 0
        failed_articles = 0
        selenium_used_count = 0
        
        for i, article in enumerate(new_articles_to_process, 1):
            try:
                result = self.article_processor.process_single_article(
                    article, i, len(new_articles_to_process)
                )
                processed_articles.append(result)
                
                if result['success']:
                    successful_articles += 1
                else:
                    failed_articles += 1
                
                if result.get('used_selenium', False):
                    selenium_used_count += 1
                
                # Add delay to be respectful to the websites
                time.sleep(Settings.DELAY_BETWEEN_REQUESTS)
                
            except Exception as e:
                print(f"   ❌ Critical error processing article {i}, skipping: {str(e)[:100]}...")
                failed_articles += 1
                continue
        
        # Combine existing articles with newly processed ones
        all_articles = existing_articles + processed_articles
        
        print(f"\n📈 Processing Complete:")
        print(f"   ✅ New successful articles: {successful_articles}")
        print(f"   ❌ New failed articles: {failed_articles}")
        print(f"   🔧 Selenium used for: {selenium_used_count} new articles")
        print(f"   📊 Total articles in database: {len(all_articles)}")
        
        return all_articles
    
    def save_results(self, articles):
        """Save articles to JSON file"""
        filename = Settings.get_full_json_path()
        return self.file_handler.save_to_json(articles, filename)
    
    def print_report(self, articles):
        """Print final report"""
        print("\n" + "=" * 50)
        print("📊 FINAL REPORT")
        print("=" * 50)
        
        successful = len([a for a in articles if a.get('success', False)])
        failed = len([a for a in articles if not a.get('success', False)])
        selenium_used = len([a for a in articles if a.get('used_selenium', False)])
        
        print(f"✅ Successful articles: {successful}")
        print(f"❌ Failed articles: {failed}")
        print(f"🔧 Selenium used: {selenium_used}")
        print(f"📊 Total in database: {len(articles)}")
        
        sources = {}
        for article in articles:
            sources[article['source']] = sources.get(article['source'], 0) + 1
        
        for source, count in sources.items():
            print(f"   📰 {source}: {count} articles")
        
        # Print sample successful article with AI features
        successful_articles = [a for a in articles if a.get('success', False) and a.get('ai_summary')]
        if successful_articles:
            print(f"\n🎯 SAMPLE AI-ENHANCED ARTICLE:")
            sample = successful_articles[-1]
            print(f"   Title: {sample['title']}")
            print(f"   Source: {sample['source']}")
            print(f"   AI Summary: {sample.get('ai_summary', 'N/A')}")
            print(f"   Keywords: {', '.join(sample.get('keywords', []))}")
            print(f"   Used Selenium: {sample.get('used_selenium', False)}")
        else:
            print(f"\n⚠️  No AI-enhanced articles to display")

def main():
    # Get Groq API key from environment variable or user input
    groq_api_key = Settings.GROQ_API_KEY
    if not groq_api_key:
        print("🔑 Enter your Groq API key (or set GROQ_API_KEY environment variable):")
        groq_api_key = input().strip()
        if not groq_api_key:
            print("⚠️  No Groq API key provided. AI features will be disabled.")
    
    scraper = NewsScraper(groq_api_key=groq_api_key)
    
    print("=" * 60)
    print("📰 ENHANCED NEWS SCRAPER - THE HINDU & TIMES OF INDIA")
    print("🤖 AI-Powered Summaries & Keywords")
    print("💾 Daily JSON Files with Duplicate Prevention")
    print("=" * 60)
    
    try:
        # Scrape news
        articles = scraper.scrape_news()
        
        # Save to JSON
        filename = scraper.save_results(articles)
        
        # Print report
        scraper.print_report(articles)
        print(f"💾 Results saved to: {filename}")
            
    except Exception as e:
        print(f"❌ Critical error in main execution: {e}")

if __name__ == "__main__":
    main()