class DuplicateChecker:
    @staticmethod
    def is_duplicate_article(new_article, existing_articles):
        """Check if article with same title already exists"""
        new_title = new_article['title'].strip().lower()
        
        for existing_article in existing_articles:
            existing_title = existing_article['title'].strip().lower()
            
            # Exact match
            if new_title == existing_title:
                return True
            
            # Similarity check for longer titles
            if len(new_title) > 20 and len(existing_title) > 20:
                similarity = DuplicateChecker._calculate_similarity(new_title, existing_title)
                if similarity > 0.7:  # 70% similarity threshold
                    return True
        
        return False
    
    @staticmethod
    def _calculate_similarity(title1, title2):
        """Calculate similarity between two titles"""
        words1 = set(title1.split())
        words2 = set(title2.split())
        common_words = words1.intersection(words2)
        return len(common_words) / max(len(words1), len(words2))
    
    @staticmethod
    def filter_new_articles(scraped_articles, existing_articles):
        """Filter out articles that already exist"""
        new_articles = []
        duplicate_count = 0
        
        for article in scraped_articles:
            if not DuplicateChecker.is_duplicate_article(article, existing_articles):
                new_articles.append(article)
            else:
                duplicate_count += 1
                print(f"   ⏭️  Skipping duplicate: {article['title'][:60]}...")
        
        print(f"📊 Filtered {duplicate_count} duplicate articles")
        return new_articles