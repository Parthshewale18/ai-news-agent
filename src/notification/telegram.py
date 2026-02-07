"""
Telegram Bot Integration
Handles user subscriptions and news delivery
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from sqlalchemy.orm import Session
from src.storage.database import SessionLocal, Subscriber
from datetime import datetime
from config.settings import settings
from typing import List
import asyncio


class TelegramNotifier:
    """Telegram bot for news notifications"""
    
    def __init__(self):
        """Initialize Telegram bot"""
        self.token = settings.telegram_bot_token
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up command handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("stop", self.stop_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - subscribe user"""
        chat_id = str(update.effective_chat.id)
        user = update.effective_user
        
        # Add subscriber to database
        db = SessionLocal()
        try:
            # Check if already subscribed
            existing = db.query(Subscriber).filter(Subscriber.chat_id == chat_id).first()
            
            if existing:
                if existing.is_active:
                    await update.message.reply_text (
                        "✅ You're already subscribed to AI News updates!\n\n"
                        "Use /stop to unsubscribe.\n"
                        "Use /help for more options."
                    )
                else:
                    # Reactivate subscription
                    existing.is_active = True
                    existing.subscribed_at = datetime.utcnow()
                    existing.unsubscribed_at = None
                    db.commit()
                    
                    await update.message.reply_text(
                        "🎉 Welcome back! Your subscription has been reactivated.\n\n"
                        "You'll now receive verified AI news updates."
                    )
            else:
                # New subscriber
                subscriber = Subscriber(
                    chat_id=chat_id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                db.add(subscriber)
                db.commit()
                
                # Welcome message
                welcome_message = (
                    "🤖 *Welcome to AI News Alert Bot!*\n\n"
                    "You'll receive instant notifications for verified AI news:\n\n"
                    "✅ Completely FREE\n"
                    "✅ No spam, only quality news\n"
                    "✅ 3-5 updates per day\n"
                    "✅ Unsubscribe anytime with /stop\n\n"
                    "*What you'll get:*\n"
                    "• Major AI model releases\n"
                    "• AI research breakthroughs\n"
                    "• AI policy updates\n"
                    "• Industry news\n\n"
                    "News is verified from trusted sources like OpenAI, Google AI, MIT Tech Review, and more.\n\n"
                    "Use /help to see all commands."
                )
                
                await update.message.reply_text(
                    welcome_message,
                    parse_mode=ParseMode.MARKDOWN
                )
                
                print(f"✅ New subscriber: {user.username or user.first_name} ({chat_id})")
                
        except Exception as e:
            print(f"❌ Error in start_command: {e}")
            await update.message.reply_text(
                "⚠️ Sorry, there was an error processing your subscription. Please try again."
            )
        finally:
            db.close()
    
    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command - unsubscribe user"""
        chat_id = str(update.effective_chat.id)
        
        db = SessionLocal()
        try:
            subscriber = db.query(Subscriber).filter(Subscriber.chat_id == chat_id).first()
            
            if subscriber and subscriber.is_active:
                subscriber.is_active = False
                subscriber.unsubscribed_at = datetime.utcnow()
                db.commit()
                
                await update.message.reply_text(
                    "👋 You've been unsubscribed from AI News updates.\n\n"
                    "To resubscribe, just send /start anytime.\n\n"
                    "We're sad to see you go!"
                )
                
                print(f"❌ Unsubscribed: {chat_id}")
            else:
                await update.message.reply_text(
                    "You're not currently subscribed.\n\n"
                    "Send /start to subscribe to AI news updates!"
                )
                
        except Exception as e:
            print(f"❌ Error in stop_command: {e}")
            await update.message.reply_text(
                "⚠️ Sorry, there was an error processing your request. Please try again."
            )
        finally:
            db.close()
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "🤖 *AI News Alert Bot - Help*\n\n"
            "*Commands:*\n"
            "/start - Subscribe to AI news updates\n"
            "/stop - Unsubscribe from updates\n"
            "/status - Check your subscription status\n"
            "/help - Show this help message\n\n"
            "*About:*\n"
            "This bot delivers verified AI news from trusted sources "
            "like OpenAI, Google AI, Meta, Anthropic, and reputable media outlets.\n\n"
            "*Features:*\n"
            "• 100% free and open source\n"
            "• No spam or ads\n"
            "• Credibility-verified news only\n"
            "• Simple, non-technical summaries\n\n"
            "*Frequency:*\n"
            "Typically 3-5 meaningful updates per day.\n\n"
            "*Privacy:*\n"
            "We only store your chat ID to send notifications. "
            "No personal data is shared or sold.\n\n"
            "Questions? Contact: @YourUsername"
        )
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        chat_id = str(update.effective_chat.id)
        
        db = SessionLocal()
        try:
            subscriber = db.query(Subscriber).filter(Subscriber.chat_id == chat_id).first()
            
            if subscriber and subscriber.is_active:
                status_text = (
                    f"✅ *Subscription Active*\n\n"
                    f"Subscribed since: {subscriber.subscribed_at.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
                    f"You're receiving verified AI news updates!"
                )
            elif subscriber:
                status_text = (
                    f"❌ *Subscription Inactive*\n\n"
                    f"Unsubscribed on: {subscriber.unsubscribed_at.strftime('%Y-%m-%d %H:%M UTC') if subscriber.unsubscribed_at else 'Unknown'}\n\n"
                    f"Send /start to resubscribe!"
                )
            else:
                status_text = (
                    "📭 *Not Subscribed*\n\n"
                    "You're not currently subscribed to AI news updates.\n\n"
                    "Send /start to subscribe!"
                )
            
            await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            print(f"❌ Error in status_command: {e}")
            await update.message.reply_text("⚠️ Error checking status. Please try again.")
        finally:
            db.close()
    
    async def send_news_notification(self, chat_id: str, article: dict, summary: dict) -> bool:
        """
        Send news notification to a single subscriber
        
        Args:
            chat_id: Telegram chat ID
            article: Article data
            summary: Gemini-generated summary
            
        Returns:
            Success status
        """
        try:
            # Format message
            message = (
                f"🤖 *AI News Alert*\n\n"
                f"{summary.get('headline', article['title'])}\n\n"
                f"*Why it matters:*\n"
                f"{summary.get('why_matters', 'Significant development in AI.')}\n\n"
                f"*Source:*\n{article['source_name']}\n\n"
                f"⏰ {article['published_at'].strftime('%b %d, %Y - %I:%M %p UTC')}\n\n"
                f"[Read More]({article['url']})"
            )
            
            # Send message
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send notification to {chat_id}: {e}")
            return False
    
    async def broadcast_news(self, article: dict, summary: dict) -> int:
        """
        Broadcast news to all active subscribers
        
        Returns:
            Number of successful sends
        """
        db = SessionLocal()
        try:
            # Get all active subscribers
            subscribers = db.query(Subscriber).filter(Subscriber.is_active == True).all()
            
            print(f"📤 Broadcasting to {len(subscribers)} subscribers...")
            
            # Send to all subscribers
            tasks = []
            for subscriber in subscribers:
                task = self.send_news_notification(subscriber.chat_id, article, summary)
                tasks.append(task)
            
            # Execute all sends concurrently
            results = await asyncio.gather(*tasks)
            
            success_count = sum(results)
            print(f"✅ Successfully sent to {success_count}/{len(subscribers)} subscribers")
            
            return success_count
            
        except Exception as e:
            print(f"❌ Error in broadcast_news: {e}")
            return 0
        finally:
            db.close()
    
    async def start(self):
        """Start the bot"""
        print("🤖 Starting Telegram bot polling...")
        await self.application.initialize()
        await self.application.start()
        # Ensure no webhook is active (conflict with polling)
        await self.application.bot.delete_webhook()
        await self.application.updater.start_polling()
        print("✅ Telegram bot polling started")
    
    async def stop(self):
        """Stop the bot"""
        print("🤖 Stopping Telegram bot...")
        if self.application.updater:
            await self.application.updater.stop()
        if self.application:
            await self.application.stop()
            await self.application.shutdown()


if __name__ == "__main__":
    # Test the bot
    bot = TelegramNotifier()
    bot.run()
