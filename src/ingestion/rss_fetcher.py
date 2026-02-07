"""
RSS Feed Fetcher
Fetches news articles from RSS feeds of trusted sources
"""

import feedparser
import yaml
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path


class RSSFetcher:
    """Fetches news from RSS feeds"""
    
    def __init__(self, sources_file: str = "config/sources.yaml"):
        """Initialize with sources configuration"""
        self.sources = self._load_sources(sources_file)
        
    def _load_sources(self, sources_file: str) -> Dict:
        """Load sources from YAML file"""
        sources_path = Path(sources_file)
        if not sources_path.exists():
            print(f"⚠️ Sources file not found: {sources_file}")
            return {}
            
        with open(sources_path, 'r') as f:
            return yaml.safe_load(f)
    
    def fetch_from_source(self, source_name: str, source_config: Dict) -> List[Dict]:
        """Fetch articles from a single RSS source"""
        articles = []
        
        if 'rss' not in source_config:
            return articles
            
        try:
            feed = feedparser.parse(source_config['rss'])
            
            for entry in feed.entries:
                # Parse published date
                published_at = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_at = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_at = datetime(*entry.updated_parsed[:6])
                else:
                    published_at = datetime.utcnow()
                
                # Only get recent articles (last 48 hours)
                if published_at < datetime.utcnow() - timedelta(hours=48):
                    continue
                
                article = {
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'published_at': published_at,
                    'source_name': source_config['name'],
                    'source_url': source_config['url'],
                    'source_domain': self._extract_domain(source_config['url']),
                    'credibility': source_config.get('credibility', 80)
                }
                
                articles.append(article)
                
            print(f"✅ Fetched {len(articles)} articles from {source_name}")
            
        except Exception as e:
            print(f"❌ Error fetching from {source_name}: {e}")
            
        return articles
    
    def fetch_all_official_sources(self) -> List[Dict]:
        """Fetch from all official company blogs"""
        all_articles = []
        
        official_sources = self.sources.get('official_sources', {})
        for source_id, source_config in official_sources.items():
            articles = self.fetch_from_source(source_id, source_config)
            all_articles.extend(articles)
            
        print(f"📰 Total articles from official sources: {len(all_articles)}")
        return all_articles
    
    def fetch_all_media_outlets(self) -> List[Dict]:
        """Fetch from all media outlets"""
        all_articles = []
        
        media_outlets = self.sources.get('media_outlets', {})
        for source_id, source_config in media_outlets.items():
            articles = self.fetch_from_source(source_id, source_config)
            all_articles.extend(articles)
            
        print(f"📰 Total articles from media outlets: {len(all_articles)}")
        return all_articles
    
    def fetch_all(self) -> List[Dict]:
        """Fetch from all sources"""
        all_articles = []
        
        # Fetch from official sources
        all_articles.extend(self.fetch_all_official_sources())
        
        # Fetch from media outlets
        all_articles.extend(self.fetch_all_media_outlets())
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        print(f"📊 Total unique articles: {len(unique_articles)} (removed {len(all_articles) - len(unique_articles)} duplicates)")
        
        return unique_articles
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc


if __name__ == "__main__":
    # Test the fetcher
    fetcher = RSSFetcher()
    articles = fetcher.fetch_all()
    
    if articles:
        print(f"\n📄 Sample article:")
        print(f"Title: {articles[0]['title']}")
        print(f"Source: {articles[0]['source_name']}")
        print(f"URL: {articles[0]['url']}")
