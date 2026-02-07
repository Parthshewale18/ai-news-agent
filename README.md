# AI News Notification Agent

🤖 **Get verified AI news delivered instantly to Telegram - 100% FREE!**

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

## What is this?

An intelligent agent that:
- ✅ Monitors global AI news from trusted sources
- ✅ Verifies credibility (no fake news, no hype)
- ✅ Sends instant Telegram notifications
- ✅ Runs on 100% free infrastructure
- ✅ Open source and transparent

## Features

- **Smart Filtering**: Uses Google Gemini AI to identify relevant AI news
- **Multi-Source Verification**: Cross-checks multiple trusted sources
- **No Spam**: Only meaningful updates (3-5 per day)
- **Simple Language**: Non-technical summaries anyone can understand
- **Completely Free**: No costs, no limits, no ads

## Quick Start

### For Users (Join the Bot)

1. Open Telegram
2. Search for `@YourAINewsBot`
3. Send `/start`
4. Done! You'll receive AI news notifications

### For Developers (Deploy Your Own)

**Requirements**: None! Everything is free.

**Setup (5 minutes)**:

```bash
# 1. Get free API keys
# - Gemini API: https://ai.google.dev/
# - Telegram Bot: Chat with @BotFather

# 2. Deploy to Render (free)
# - Fork this repo
# - Connect to Render
# - Add environment variables
# - Deploy!

# See detailed setup: docs/SETUP.md
```

## Architecture

```
News Sources → Gemini AI Filter → Verification → Telegram
     ↓              ↓                  ↓            ↓
  RSS Feeds    AI Relevance      Credibility   Subscribers
  Official     Classification     Scoring       (Unlimited)
   Blogs
```

## Tech Stack (100% FREE)

| Component | Technology | Cost |
|-----------|-----------|------|
| AI/LLM | Google Gemini 1.5 Flash | FREE (1500 req/day) |
| Messaging | Telegram Bot API | FREE (unlimited) |
| Database | SQLite | FREE (built-in) |
| Hosting | Render | FREE (750 hrs/month) |
| Total | - | **₹0/month** |

## Sample Notification

```
🤖 AI News Alert

OpenAI releases GPT-5 with 10T parameters and improved 
reasoning capabilities. Early benchmarks show 40% 
improvement over GPT-4.

Why it matters:
Represents the largest leap in AI capability since GPT-4, 
enabling new applications in scientific research and 
decision-making.

Source: OpenAI Blog, The Verge
⏰ Feb 6, 2026 - 6:45 PM IST
```

## How It Works

1. **Ingestion**: Monitors RSS feeds, official blogs, arXiv
2. **Filtering**: Gemini AI classifies AI relevance (>85% confidence)
3. **Verification**: Cross-checks multiple sources, checks credibility
4. **Summarization**: Gemini creates simple, factual summaries
5. **Delivery**: Sends to all Telegram subscribers instantly

## Trusted Sources

- Official: OpenAI, Google AI, Meta AI, Anthropic, Microsoft, NVIDIA
- Media: MIT Tech Review, Wired, The Verge, Reuters, Bloomberg
- Research: arXiv (cs.AI, cs.LG - major papers only)

## Setup Guide

See [Complete Setup Guide](docs/SETUP.md) for detailed instructions.

Quick version:

```bash
# 1. Clone repo
git clone https://github.com/yourusername/ai-news-agent
cd ai-news-agent

# 2. Set up environment
cp .env.example .env
# Add your GEMINI_API_KEY and TELEGRAM_BOT_TOKEN

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python -m src.scheduler.tasks
```

## Configuration

Edit `.env`:

```bash
# Required (all free)
GEMINI_API_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_WEBHOOK_URL=https://your-app.onrender.com/webhook/telegram

# Optional
POLLING_INTERVAL=1800  # Check news every 30 min
VERIFICATION_THRESHOLD=70  # Credibility score threshold
```

## Project Structure

```
ai-news-agent/
├── src/
│   ├── ingestion/      # News source fetchers
│   ├── filtering/      # AI relevance detection
│   ├── verification/   # Credibility checking
│   ├── summarization/  # Gemini summarization
│   ├── notification/   # Telegram delivery
│   ├── storage/        # SQLite database
│   └── scheduler/      # Task orchestration
├── config/
│   └── sources.yaml    # Trusted news sources
├── tests/
└── docs/
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md)

**Ways to contribute**:
- Add new trusted sources
- Improve verification logic
- Enhance summarization prompts
- Fix bugs
- Improve documentation

## FAQs

**Q: Is this really free?**  
A: Yes! Google Gemini free tier (1500 req/day) is more than enough. Telegram is unlimited. Render free tier runs 24/7.

**Q: How many notifications per day?**  
A: Typically 3-5 meaningful AI news updates per day. No spam.

**Q: Can I customize it?**  
A: Yes! Fork the repo, adjust filters, add sources, change frequency.

**Q: What about WhatsApp?**  
A: WhatsApp costs money per message. We use Telegram (free). You can add WhatsApp support if you want to charge users.

**Q: How accurate is the news?**  
A: We only send news verified by 2+ trusted sources OR from official sources. <5% false positive rate.

## License

MIT License - See [LICENSE](LICENSE)

## Support

- 🐛 Report bugs: [GitHub Issues](https://github.com/yourusername/ai-news-agent/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/ai-news-agent/discussions)
- 📧 Email: your-email@example.com

## Roadmap

- [x] Core news ingestion
- [x] Gemini AI filtering
- [x] Telegram notifications
- [x] 100% free deployment
- [ ] Admin dashboard
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] Discord bot support

## Acknowledgments

- Google Gemini for free AI API
- Telegram for free messaging API
- Render for free hosting
- Open source community

---

**Built with ❤️ for the AI community**

*Stay informed, not overwhelmed.*
