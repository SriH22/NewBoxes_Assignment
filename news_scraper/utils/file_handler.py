import json
import os
from datetime import datetime

class FileHandler:
    @staticmethod
    def load_existing_articles(filename):
        """Load existing articles from JSON file"""
        if not os.path.exists(filename):
            return []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('articles', [])
        except Exception as e:
            print(f"⚠️  Error loading existing file: {e}")
            return []
    
    @staticmethod
    def save_to_json(articles, filename, metadata=None):
        """Save articles to JSON file"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        if metadata is None:
            successful_articles = [a for a in articles if a.get('success', False)]
            failed_articles = [a for a in articles if not a.get('success', False)]
            selenium_used = [a for a in articles if a.get('used_selenium', False)]
            
            metadata = {
                'total_articles': len(articles),
                'successful_articles': len(successful_articles),
                'failed_articles': len(failed_articles),
                'selenium_used': len(selenium_used),
                'sources': list(set(article['source'] for article in articles)),
                'generated_at': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'updated_at': datetime.now().isoformat()
            }
        
        output = {
            'metadata': metadata,
            'articles': articles
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(articles)} articles to {filename}")
        return filename