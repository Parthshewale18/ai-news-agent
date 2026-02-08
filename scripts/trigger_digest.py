
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.scheduler.tasks import NewsAgentScheduler

async def trigger():
    agent = NewsAgentScheduler()
    print("Step 2: Running Daily Digest...")
    await agent.run_daily_digest()
    print("✅ Digest triggered")
    # No need to stop if updater not running
    # await agent.telegram.stop() 

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(trigger())
