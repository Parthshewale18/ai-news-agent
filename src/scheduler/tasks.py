"""
Main News Pipeline Scheduler
Orchestrates the complete flow: Ingest → Filter → Summarize → Notify
"""

import asyncio
import time
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.ingestion.rss_fetcher import RSSFetcher
from src.filtering.ai_classifier import AIRelevanceFilter
from src.summarization.llm_summarizer import NewsSummarizer
from src.notification.telegram import TelegramNotifier
from src.storage.database import SessionLocal, Article, init_db
from config.settings import settings


class NewsAgentScheduler:
    """Main scheduler for AI News Agent"""
    
    def __init__(self):
        """Initialize all components"""
        print("🚀 Initializing AI News Agent...")
        
        # Initialize database
        init_db()
        
        # Initialize components
        self.rss_fetcher = RSSFetcher()
        self.ai_filter = AIRelevanceFilter()
        self.summarizer = NewsSummarizer()
        self.telegram = TelegramNotifier()
        
        # Scheduler
        self.scheduler = AsyncIOScheduler()
        
        print("✅ All components initialized")
    
    async def process_single_article(self, article_data: dict) -> bool:
        """
        Process a single article through the pipeline
        
        Returns:
            True if article was sent, False otherwise
        """
        db = SessionLocal()
        try:
            # Check if already processed
            existing = db.query(Article).filter(Article.url == article_data['url']).first()
            if existing:
                return False  # Already processed
            
            # Step 1: Check AI relevance
            is_relevant, confidence, reasoning = self.ai_filter.is_ai_relevant(article_data)
            
            # Create article record
            article = Article(
                title=article_data['title'],
                url=article_data['url'],
                source_name=article_data['source_name'],
                source_domain=article_data['source_domain'],
                published_at=article_data['published_at'],
                content=article_data.get('summary', ''),
                is_ai_relevant=is_relevant,
                ai_confidence=confidence,
                credibility_score=article_data.get('credibility', 80),
                is_verified=True if article_data.get('credibility', 0) >= 90 else False,
                verification_reason=reasoning
            )
            
            db.add(article)
            db.commit()
            
            if not is_relevant:
                return False  # Not AI-related
            
            # Step 2: Generate summary
            print(f"📝 Summarizing: {article_data['title'][:60]}...")
            summary = self.summarizer.summarize(article_data)
            article.summary = f"{summary['headline']}\n\n{summary['why_matters']}"
            db.commit()
            
            # Step 3: Send notifications
            print(f"📤 Broadcasting to subscribers...")
            success_count = await self.telegram.broadcast_news(
                article_data,
                summary
            )
            
            if success_count > 0:
                article.notification_sent = True
                article.sent_at = datetime.utcnow()
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error processing article: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            db.close()
    
    async def run_news_pipeline(self):
        """Run the complete news pipeline"""
        print("\n" + "="*60)
        print(f"🔄 Running news pipeline at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
        try:
            # Step 1: Fetch articles
            print("📡 Fetching articles from RSS feeds...")
            articles = self.rss_fetcher.fetch_all()
            print(f"📊 Fetched {len(articles)} articles\n")
            
            if not articles:
                print ("⚠️ No new articles found")
                return
            
            # Step 2: Process each article
            sent_count = 0
            for i, article_data in enumerate(articles[:settings.max_articles_per_cycle], 1):
                print(f"[{i}/{len(articles)}] Processing: {article_data['title'][:60]}...")
                
                was_sent = await self.process_single_article(article_data)
                if was_sent:
                    sent_count += 1
                    
                # Small delay to avoid rate limits
                await asyncio.sleep(2)
            
            print(f"\n✅ Pipeline complete! Sent {sent_count} notifications")
            
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            import traceback
            traceback.print_exc()
    
    async def start(self):
        """Start the scheduler"""
        print("\n🤖 Starting AI News Agent Scheduler...")
        print(f"⏰ Polling interval: {settings.polling_interval} seconds ({settings.polling_interval // 60} minutes)")
        print(f"🎯 AI relevance threshold: {settings.ai_relevance_threshold}%")
        print(f"✅ Credibility threshold: {settings.verification_threshold}%\n")
        
        # Run immediately on startup
        asyncio.create_task(self.run_news_pipeline())
        
        # Schedule periodic runs
        self.scheduler.add_job(
            self.run_news_pipeline,
            IntervalTrigger(seconds=settings.polling_interval),
            id='news_pipeline',
            name='News Pipeline',
            replace_existing=True
        )
        
        # Start scheduler
        self.scheduler.start()
        print("✅ Scheduler started successfully!\n")
        
        # Also run the Telegram bot
        print("🤖 Starting Telegram bot...")
        await self.telegram.start()


async def main():
    """Main entry point"""
    agent = NewsAgentScheduler()
    await agent.start()
    
    # Keep running
    try:
        # Event loop needed for Telegram updater
        stop_event = asyncio.Event()
        await stop_event.wait()
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Shutting down gracefully...")
        # Cleanup
        await agent.telegram.stop()
        agent.scheduler.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
