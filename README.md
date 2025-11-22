# NewBoxes_Assignment
Ai Based News Feed Application POC

Link for Figma MockUp : https://ounce-planet-36653332.figma.site/

A Python tool that automatically scrapes news various sources, generates AI summaries using Groq, and stores articles in organized JSON files.

🚀 Quick Start
1. Install Dependencies : pip install requests beautifulsoup4 newspaper3k selenium groq webdriver-manager
  
2. Setup Groq API Or enter when prompted
   
3. Run the Script : python main.py

# Once you run the backend script now run the ui.py script from the same directory, it takes the json folder location as the input so chnage the location 
# also Enter your groq key in the top in ui.py
   
📁 Project Structure
text
news_scraper/
├── main.py                      # Entry point
├── config/settings.py           # Configuration
├── scraper/                     # News source scrapers
├── services/groq_service.py     # AI integration
├── utils/                       # Helper functions
└── output/                      # Generated JSON files

✨ Features
📰 For exmaple this code Scrapes The Hindu & Times of India

📊 Output
Creates output/news_articles_YYYY-MM-DD.json

⚠️ Notes
Requires Chrome browser

