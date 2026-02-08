"""
News Summarizer using Gemini
Generates concise, non-technical summaries for Telegram
"""

import google.generativeai as genai
import json
from typing import Dict, List
from config.settings import settings


class NewsSummarizer:
    """Summarize news articles using Gemini"""
    
    def __init__(self):
        """Initialize Gemini model"""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def summarize(self, article: Dict) -> Dict:
        """
        Generate summary for article
        
        Returns:
            {
                'headline': '...',
                'why_matters': '...'
            }
        """
        prompt = f"""
You are summarizing AI news for a general audience (non-technical users).

Article Title: {article.get('title', '')}
Article Summary: {article.get('summary', '')[:1000]}

Create a notification with:

1. Headline (1-2 sentences, factual, no hype)
2. Why it matters (1-2 sentences explaining impact in simple terms)

Requirements:
- Use simple language (no jargon like "parameters", "tokens", etc.)
- Explain any technical terms you must use
- Be neutral and factual
- No speculation or opinion
- Keep under 150 words total
- Focus on real-world impact

Respond ONLY with valid JSON in this format:
{{
    "headline": "clear, factual headline here",
    "why_matters": "simple explanation of impact"
}}
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Low creativity, factual
                )
            )
            
            # Parse JSON response
            text = response.text.strip()
            # Handle potential markdown code blocks
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
                
            result = json.loads(text)
            
            return {
                'headline': result.get('headline', article['title']),
                'why_matters': result.get('why_matters', 'Significant development in AI.')
            }
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse Gemini summary as JSON: {e}")
            print(f"Response: {response.text}")
            # Fallback to original title
            return {
                'headline': article['title'],
                'why_matters': 'Significant development in the AI field.'
            }
        except Exception as e:
            print(f"❌ Summarization error: {e}")
            return {
                'headline': article['title'],
                'why_matters': 'Significant development in the AI field.'
            }

    def generate_daily_digest(self, articles: List[Dict]) -> Dict:
        """
        Generate a daily digest from a list of articles
        
        Returns:
            {
                'intro': '...',
                'items': [
                    {'id': 123, 'headline': '...', 'impact': '...'}
                ],
                'outro': '...'
            }
        """
        if not articles:
            return None
            
        articles_text = ""
        for i, art in enumerate(articles[:10], 1):  # Limit to top 10 to fit context
            summary_text = art.summary[:200] if art.summary else "No summary available."
            articles_text += f"ID: {art.id}\nTitle: {art.title}\nSummary: {summary_text}\n\n"
            
        prompt = f"""
You are writing a Daily AI News Digest for a Telegram channel.
Here are the top stories from the last 24 hours:

{articles_text}

Task:
1. Select the top 3-5 most important stories.
2. Write a short 1-sentence headline for each.
3. Write a very brief 1-sentence impact statement for each.
4. Write a catchy intro (e.g., "Good morning! Here's what happened in AI today:")
5. Write a brief outro.

Respond ONLY with valid JSON in this format:
{{
    "intro": "Good morning! ...",
    "items": [
        {{
            "id": 123, 
            "headline": "headline here",
            "impact": "impact here"
        }}
    ],
    "outro": "Stay tuned for more!"
}}
"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                )
            )
            
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
                
            return json.loads(text)
            
        except Exception as e:
            print(f"❌ Digest generation error: {e}")
            return None


if __name__ == "__main__":
    # Test the summarizer
    summarizer = NewsSummarizer()
    
    test_article = {
        'title': 'OpenAI Releases GPT-5 with 10 Trillion Parameters',
        'summary': 'OpenAI today announced GPT-5, their most powerful language model yet with 10 trillion parameters. It shows significant improvements in reasoning, math, and coding tasks compared to GPT-4...'
    }
    
    print("Testing summarizer...")
    result = summarizer.summarize(test_article)
    print(f"\nHeadline: {result['headline']}")
    print(f"\nWhy it matters: {result['why_matters']}")
