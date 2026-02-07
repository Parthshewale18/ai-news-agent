"""
News Summarizer using Gemini
Generates concise, non-technical summaries for Telegram
"""

import google.generativeai as genai
import json
from typing import Dict
from config.settings import settings


class NewsSummarizer:
    """Summarize news articles using Gemini"""
    
    def __init__(self):
        """Initialize Gemini model"""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
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
            result = json.loads(response.text.strip())
            
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
