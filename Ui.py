import streamlit as st
import json
import requests
from datetime import datetime
import os
from groq import Groq


current_date = datetime.now().strftime('%Y-%m-%d')

# Initialize Groq client
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

def load_news_data(json_file_path):
    """Load news data from JSON file"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        st.error(f"JSON file not found at path: {json_file_path}")
        return {"articles": []}
    except json.JSONDecodeError:
        st.error(f"Invalid JSON file at path: {json_file_path}")
        return {"articles": []}
    except Exception as e:
        st.error(f"Error loading JSON file: {e}")
        return {"articles": []}

def search_articles(query, articles):
    """Search articles based on query using Groq API"""
    try:
        # Prepare context from articles
        context = "\n\n".join([
            f"Title: {article['title']}\nSummary: {article['ai_summary']}\nKeywords: {', '.join(article.get('keywords', []))}"
            for article in articles
        ])
        
        # Create prompt for Groq
        prompt = f"""
        Based on the following news articles and the user query, find the most relevant articles.
        
        Available Articles:
        {context}
        
        User Query: {query}
        
        Return only the indices of the most relevant articles (0-based) in a list format. Be precise and only return articles that directly match the query.
        """
        
        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful news search assistant. Return only the indices of relevant articles in list format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=50
        )
        
        response = chat_completion.choices[0].message.content.strip()
        
        # Parse the response to get indices
        try:
            if "[" in response and "]" in response:
                indices_str = response[response.index("["):response.index("]")+1]
                indices = eval(indices_str)
                return [articles[i] for i in indices if i < len(articles)]
            else:
                return keyword_search(query, articles)
        except:
            return keyword_search(query, articles)
            
    except Exception as e:
        st.error(f"Search error: {e}")
        return keyword_search(query, articles)

def keyword_search(query, articles):
    """Fallback keyword-based search"""
    query_lower = query.lower()
    relevant_articles = []
    
    for article in articles:
        # Check title, summary, and keywords
        article_keywords = article.get('keywords', [])
        if (query_lower in article['title'].lower() or 
            query_lower in article.get('ai_summary', '').lower() or
            any(query_lower in str(keyword).lower() for keyword in article_keywords)):
            relevant_articles.append(article)
    
    return relevant_articles

def filter_by_favorites(articles, favorite_subjects):
    """Filter articles based on favorite subjects"""
    if not favorite_subjects:
        return articles
    
    filtered_articles = []
    for article in articles:
        # Check if any favorite subject matches article keywords or title/summary
        article_text = f"{article['title']} {article.get('ai_summary', '')} {' '.join(article.get('keywords', []))}".lower()
        if any(subject.lower() in article_text for subject in favorite_subjects):
            filtered_articles.append(article)
    
    return filtered_articles

def display_article_summary(article, index):
    """Display article summary in feed format"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.subheader(article['title'])
        st.write(f"**Source:** {article.get('source', 'Unknown')}")
        st.write(f"**Date:** {article.get('date', 'Unknown')}")
        
        # Display AI summary
        st.write("**Summary:**")
        st.write(article.get('ai_summary', 'No summary available'))
        
        # Display keywords
        keywords = article.get('keywords', [])
        if keywords:
            st.write("**Keywords:**", ", ".join(keywords[:5]))  # Show first 5 keywords
    
    with col2:
        if st.button("Read More", key=f"read_{index}"):
            st.session_state.selected_article = article

def display_full_article(article):
    """Display full article content"""
    st.header(article['title'])
    st.write(f"**Source:** {article.get('source', 'Unknown')}")
    st.write(f"**Date:** {article.get('date', 'Unknown')}")
    st.write(f"**Published:** {article.get('published_date', 'Unknown')}")
    
    # Display full text if available, otherwise show summary
    if article.get('text'):
        st.write("**Full Article:**")
        st.write(article['text'])
    else:
        st.write("**Summary:**")
        st.write(article.get('ai_summary', 'No content available'))
    
    # Display link
    if article.get('link'):
        st.write(f"**Original Article:** [Read here]({article['link']})")
    
    # Display keywords
    keywords = article.get('keywords', [])
    if keywords:
        st.write("**Keywords:**", ", ".join(keywords))
    
    # Back button
    if st.button("← Back to Feed"):
        st.session_state.selected_article = None

def main():
    st.set_page_config(
        page_title="News Feed App",
        page_icon="📰",
        layout="wide"
    )
    
    # Replace with your actual JSON file path
    JSON_FILE_PATH = f"news_scraper/output/news_articles_{current_date}.json"  # Update this path
    
    # Load news data
    news_data = load_news_data(JSON_FILE_PATH)
    articles = news_data.get("articles", [])
    
    # Initialize session state
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []
    if 'selected_article' not in st.session_state:
        st.session_state.selected_article = None
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "News Feed"
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    
    # Sidebar for navigation and favorites
    with st.sidebar:
        st.title("📰 News App")
        
        # Navigation
        tab = st.radio("Navigate to:", ["News Feed", "Favorites", "Manage Favorites"])
        st.session_state.current_tab = tab
        
        # Search bar in sidebar
        st.subheader("🔍 Search News")
        search_query = st.text_input("Enter search terms:")
        
        if search_query:
            if st.button("Search"):
                with st.spinner("Searching..."):
                    st.session_state.search_results = search_articles(search_query, articles)
        
        if st.button("Clear Search"):
            st.session_state.search_results = None
        
        # Display stats
        st.subheader("📊 Stats")
        st.write(f"Total Articles: {len(articles)}")
        if st.session_state.search_results is not None:
            st.write(f"Search Results: {len(st.session_state.search_results)}")
        st.write(f"Favorite Topics: {len(st.session_state.favorites)}")
    
    # Main content area
    if st.session_state.selected_article:
        # Display full article
        display_full_article(st.session_state.selected_article)
    
    else:
        # Display appropriate content based on current tab
        if st.session_state.current_tab == "News Feed":
            st.title("📰 News Feed")
            
            # Display search results or all articles
            if st.session_state.search_results is not None:
                articles_to_display = st.session_state.search_results
                st.write(f"### Search Results ({len(articles_to_display)} articles found)")
            else:
                articles_to_display = articles
                st.write(f"### Latest News ({len(articles_to_display)} articles)")
            
            if not articles_to_display:
                st.info("No articles found.")
            else:
                for i, article in enumerate(articles_to_display):
                    display_article_summary(article, i)
                    st.markdown("---")
        
        elif st.session_state.current_tab == "Favorites":
            st.title("⭐ Favorite Topics News")
            
            if not st.session_state.favorites:
                st.info("No favorite topics set. Go to 'Manage Favorites' to add some!")
            else:
                favorite_articles = filter_by_favorites(articles, st.session_state.favorites)
                st.write(f"### News matching your favorite topics ({len(favorite_articles)} articles)")
                
                if not favorite_articles:
                    st.info("No articles match your favorite topics.")
                else:
                    for i, article in enumerate(favorite_articles):
                        display_article_summary(article, i)
                        st.markdown("---")
        
        elif st.session_state.current_tab == "Manage Favorites":
            st.title("⚙️ Manage Favorite Topics")
            
            st.write("### Current Favorite Topics")
            if st.session_state.favorites:
                for i, topic in enumerate(st.session_state.favorites):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"• {topic}")
                    with col2:
                        if st.button("Remove", key=f"remove_{i}"):
                            st.session_state.favorites.remove(topic)
                            st.rerun()
            else:
                st.info("No favorite topics added yet.")
            
            st.write("### Add New Favorite Topic")
            new_topic = st.text_input("Enter a topic (e.g., 'Technology', 'Sports', 'Politics'):")
            if st.button("Add Topic") and new_topic:
                if new_topic not in st.session_state.favorites:
                    st.session_state.favorites.append(new_topic)
                    st.success(f"Added '{new_topic}' to favorites!")
                    st.rerun()
                else:
                    st.warning("Topic already in favorites!")
            
            # Show suggested topics based on article keywords
            st.write("### Suggested Topics")
            all_keywords = []
            for article in articles:
                all_keywords.extend(article.get('keywords', []))
            
            # Get unique keywords and show top ones
            unique_keywords = list(set(all_keywords))
            popular_keywords = [kw for kw in unique_keywords if all_keywords.count(kw) > 1][:10]
            
            for keyword in popular_keywords:
                if keyword not in st.session_state.favorites:
                    if st.button(f"Add '{keyword}'", key=f"add_{keyword}"):
                        st.session_state.favorites.append(keyword)
                        st.rerun()

if __name__ == "__main__":
    main()