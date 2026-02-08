"""
AI Relevance Classifier
Uses Google Gemini to determine if news is AI-related
"""

import google.generativeai as genai
import json
import yaml
from pathlib import Path
from typing import Dict, Tuple
from config.settings import settings


class AIRelevanceFilter:
    """Filter articles for AI relevance using Gemini"""
    
    def __init__(self):
        """Initialize Gemini model"""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Load keywords from sources config
        sources_path = Path("config/sources.yaml")
        if sources_path.exists():
            with open(sources_path, 'r') as f:
                sources = yaml.safe_load(f)
                self.keywords = sources.get('ai_keywords', {})
        else:
            self.keywords = self._default_keywords()
    
    def _default_keywords(self) -> Dict:
        """Default AI keywords if config not found"""
        return {
            'primary': [
                'artificial intelligence', 'machine learning', 'deep learning',
                'neural network', 'LLM', 'GPT', 'transformer', 'generative AI'
            ],
            'companies': ['OpenAI', 'Google AI', 'DeepMind', 'Meta AI', 'Anthropic', 'NVIDIA'],
            'topics': ['AI model', 'AI research', 'computer vision', 'NLP']
        }
    
    def _keyword_prefilter(self, article: Dict) -> bool:
        """Fast keyword-based pre-filter"""
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        # Check primary keywords
        for keyword in self.keywords.get('primary', []):
            if keyword.lower() in text:
                return True
        
        # Check company names
        for company in self.keywords.get('companies', []):
            if company.lower() in text:
                return True
        
        # Check topics
        for topic in self.keywords.get('topics', []):
            if topic.lower() in text:
                return True
        
        return False
    
    def classify_with_gemini(self, article: Dict) -> Tuple[bool, float, str]:
        """
        Classify article using Gemini AI
        
        Returns:
            (is_relevant, confidence, reasoning)
        """
        prompt = f"""
Classify if this news article is primarily about AI/ML technology.

Title: {article.get('title', '')}
Summary: {article.get('summary', '')[:500]}

Respond ONLY with valid JSON in this exact format:
{{
    "relevant": true/false,
    "confidence": 0-100,
    "reasoning": "brief explanation"
}}

Focus on:
- AI models and research
- Machine learning breakthroughs
- AI products and releases
- AI policy and regulation
- AI hardware

NOT relevant if it's only:
- General tech news
- Business news mentioning AI in passing
- Generic productivity tools using AI as a buzzword
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,  # Low temperature for factual classification
                )
            )
            
            # Parse JSON response
            result = json.loads(response.text.strip())
            
            is_relevant = result.get('relevant', False)
            confidence = float(result.get('confidence', 0))
            reasoning = result.get('reasoning', '')
            
            return is_relevant, confidence, reasoning
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse Gemini response as JSON: {e}")
            print(f"Response: {response.text}")
            return False, 0.0, "JSON parse error"
        except Exception as e:
            print(f"❌ Gemini classification error: {e}")
            return False, 0.0, f"Error: {str(e)}"
    
    def is_ai_relevant(self, article: Dict) -> Tuple[bool, float, str]:
        """
        Determine if article is AI-relevant
        
        Returns:
            (is_relevant, confidence, reasoning)
        """
        # Stage 1: Fast keyword pre-filter
        if not self._keyword_prefilter(article):
            return False, 0.0, "No AI keywords found"
        
        # Stage 2: Gemini AI classification
        is_relevant, confidence, reasoning = self.classify_with_gemini(article)
        
        # Only accept if confidence is above threshold
        if is_relevant and confidence >= settings.ai_relevance_threshold:
            print(f"✅ AI-relevant ({confidence}%): {article['title'][:60]}...")
            return True, confidence, reasoning
        else:
            print(f"❌ Not AI-relevant ({confidence}%): {article['title'][:60]}...")
            return False, confidence, reasoning


if __name__ == "__main__":
    # Test the classifier
    filter = AIRelevanceFilter()
    
    # Test article 1: Clearly AI-related
    test_article_1 = {
        'title': 'OpenAI Releases GPT-5 with Revolutionary Reasoning Capabilities',
        'summary': 'OpenAI today announced GPT-5, a new large language model with 10 trillion parameters...'
    }
    
    # Test article 2: Not AI-related
    test_article_2 = {
        'title': 'Apple Announces New iPhone 16',
        'summary': 'Apple unveiled the iPhone 16 today with improved camera and longer battery life...'
    }
    
    print("\n=== Test Article 1 (Should be relevant) ===")
    relevant, conf, reason = filter.is_ai_relevant(test_article_1)
    print(f"Relevant: {relevant}, Confidence: {conf}%, Reasoning: {reason}\n")
    
    print("=== Test Article 2 (Should NOT be relevant) ===")
    relevant, conf, reason = filter.is_ai_relevant(test_article_2)
    print(f"Relevant: {relevant}, Confidence: {conf}%, Reasoning: {reason}")
