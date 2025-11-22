import json
from groq import Groq
from config.settings import Settings

class GroqService:
    def __init__(self, api_key=None):
        self.client = None
        if api_key:
            self.client = Groq(api_key=api_key)
    
    def summarize_article(self, text, title):
        """Summarize article content and extract keywords using Groq API"""
        if not self.client or not text:
            return {"summary": "", "keywords": []}
        
        try:
            # Truncate text if too long
            if len(text) > Settings.MAX_CONTENT_LENGTH:
                text = text[:Settings.MAX_CONTENT_LENGTH] + "..."
            
            prompt = f"""
            Please analyze the following news article and provide:
            
            1. A concise summary (2-3 sentences)
            2. 5-7 important keywords/key phrases
            
            Article Title: {title}
            Article Content: {text}
            
            Format your response as JSON:
            {{
                "summary": "concise summary here",
                "keywords": ["keyword1", "keyword2", "keyword3"]
            }}
            """
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes news articles and extracts key information. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.1-8b-instant",
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                result = json.loads(result_text)
                return {
                    "summary": result.get("summary", ""),
                    "keywords": result.get("keywords", [])
                }
            except json.JSONDecodeError:
                print("   ⚠️  Failed to parse Groq response as JSON, using fallback")
                return {
                    "summary": result_text[:200] + "..." if len(result_text) > 200 else result_text,
                    "keywords": []
                }
                
        except Exception as e:
            print(f"   ❌ Error with Groq API: {str(e)[:100]}...")
            return {"summary": "", "keywords": []}