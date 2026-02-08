
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.scheduler.tasks import NewsAgentScheduler

async def trigger_manual_updates():
    print("🚀 Manually triggering AI News Pipeline and Daily Digest...")
    
    agent = NewsAgentScheduler()
    
    # 1. Fetch new articles (this will populate the DB with recent news)
    print("\nStep 1: Running News Pipeline (fetching articles)...")
    await agent.run_news_pipeline()
    
    # 2. Generate and send Daily Digest
    print("\nStep 2: Running Daily Digest...")
    await agent.run_daily_digest()
    
    # Clean up Telegram connection if necessary (though run_daily_digest uses its own bot instance)
    # Actually TelegramNotifier creates its own application. 
    # Let's ensure everything is closed.
    if hasattr(agent.telegram, 'stop'):
        await agent.telegram.stop()
        
    print("\n✅ Manual trigger complete!")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(trigger_manual_updates())
