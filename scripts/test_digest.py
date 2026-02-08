
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.summarization.llm_summarizer import NewsSummarizer
from src.notification.telegram import TelegramNotifier
from src.storage.database import Article

async def test_digest():
    print("🧪 Testing Daily Digest Feature...")
    
    # 1. Mock some articles
    articles = [
        Article(
            id=1,
            title="OpenAI Releases GPT-5",
            summary="OpenAI has released GPT-5 with massive improvements in reasoning.",
            url="https://openai.com/blog/gpt-5",
            source_name="OpenAI",
            source_domain="openai.com"
        ),
        Article(
            id=2,
            title="Google DeepMind Solver for Math",
            summary="DeepMind's new AI solves International Math Olympiad problems.",
            url="https://deepmind.google/math",
            source_name="DeepMind",
            source_domain="deepmind.google"
        )
    ]
    
    # 2. Generate Content
    print("\n📝 Generating content with Gemini...")
    summarizer = NewsSummarizer()
    digest = summarizer.generate_daily_digest(articles)
    
    if not digest:
        print("❌ Failed to generate digest.")
        return
        
    print(f"✅ Generated Digest:\n{digest}")
    
    # 3. Send to Telegram
    print("\n📤 Sending to Telegram...")
    telegram = TelegramNotifier()
    await telegram.start()
    
    # We need to manually insert these mock articles into DB for the "Read More" button to work
    # But for this test, we just want to see if the message sends.
    # The buttons won't work perfectly if IDs 1 and 2 don't exist in your local DB, 
    # but the message layout will be visible.
    
    await telegram.send_daily_digest(digest)
    await telegram.stop()
    print("\n✅ Test Complete!")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(test_digest())
    except KeyboardInterrupt:
        pass
