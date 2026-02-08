# Setup Guide

## Quick Start

### Prerequisites
- Python 3.11 or higher
- Free API keys (no credit card required):
  - Google Gemini API
  - Telegram Bot Token

### Step 1: Get API Keys

#### Gemini API Key (FREE)
1. Visit https://ai.google.dev/
2. Click "Get API Key"
3. Sign in with Google account
4. Create API key
5. Copy the key (starts with `AIzaSy...`)

#### Telegram Bot Token (FREE)
1. Open Telegram app
2. Search for `@BotFather`
3. Send `/newbot`
4. Choose a name: `AI News Alert`
5. Choose a username: `ai_news_alert_bot`
6. Copy the token (`123456789:ABC...`)

### Step 2: Setup Project

```bash
# Clone repository
git clone https://github.com/yourusername/ai-news-agent
cd ai-news-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy example env file
copy .env.example .env

# Edit .env and add your API keys
# GEMINI_API_KEY=your_gemini_key_here
# TELEGRAM_BOT_TOKEN=your_telegram_token_here
```

### Step 4: Initialize Database

```bash
# Initialize SQLite database
python -m src.storage.database
```

### Step 5: Run the Agent

```bash
# Start the news agent
python -m src.scheduler.tasks
```

That's it! Your bot is now running.

### Step 6: Test on Telegram

1. Open Telegram
2. Search for your bot: `@your_bot_username`
3. Send `/start`
4. You should receive a welcome message

## Deployment (Render - FREE)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/ai-news-agent
git push -u origin main
```

### 2. Deploy to Render

1. Go to https://render.com
2. Sign up (free account)
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: `ai-news-agent`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `GEMINI_API_KEY`: your Gemini key
   - `TELEGRAM_BOT_TOKEN`: your bot token
   - `TELEGRAM_WEBHOOK_URL`: `https://your-app.onrender.com/webhook/telegram`
7. Click "Create Web Service"

Your bot will be live in 2-3 minutes!

## Troubleshooting

### Bot not responding

1. Check if service is running (Render dashboard)
2. Check logs for errors
3. Verify API keys are correct in environment variables

### "ModuleNotFoundError"

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Database errors

```bash
# Reinitialize database
rm ainews.db
python -m src.storage.database
```

### Rate limit errors

- Gemini free tier: 1500 requests/day
- If exceeded, wait 24 hours or upgrade to paid tier
- Reduce `POLLING_INTERVAL` in .env

## Configuration

Edit `.env` to customize:

```bash
# Check news every 1 hour (instead of 30 min)
POLLING_INTERVAL=3600

# Only accept very high AI relevance (95%+)
AI_RELEVANCE_THRESHOLD=95

# Lower credibility threshold
VERIFICATION_THRESHOLD=60
```

## Support

- Issues: https://github.com/yourusername/ai-news-agent/issues
- Discussions: https://github.com/yourusername/ai-news-agent/discussions

## Next Steps

- Share your bot with friends
- Star the GitHub repository
- Contribute improvements
- Add more news sources
