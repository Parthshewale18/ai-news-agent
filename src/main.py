import sys
# Python 3.13 compatibility shim for feedparser (cgi module removed)
try:
    import cgi
except ImportError:
    try:
        import legacy_cgi as cgi
        sys.modules['cgi'] = cgi
    except ImportError:
        pass

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.scheduler.tasks import NewsAgentScheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent instance
agent = NewsAgentScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the lifecycle of the application.
    Starts the scheduler and Telegram bot on startup.
    Cleans up resources on shutdown.
    """
    try:
        logger.info("🚀 Starting AI News Agent via FastAPI...")
        await agent.start()
        yield
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        yield
    finally:
        logger.info("🛑 Shutting down AI News Agent...")
        try:
            await agent.telegram.stop()
            if agent.scheduler.running:
                agent.scheduler.shutdown()
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

# Create FastAPI app
app = FastAPI(
    title="AI News Agent",
    description="Automated AI News Aggregator & Telegram Bot",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def health_check():
    """
    Health check endpoint for Render.
    Returns 200 OK to signal the service is healthy.
    """
    return {
        "status": "healthy",
        "service": "ai-news-agent",
        "scheduler_running": agent.scheduler.running if hasattr(agent.scheduler, 'running') else False
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
