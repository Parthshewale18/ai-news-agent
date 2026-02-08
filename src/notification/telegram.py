"""
Telegram Bot Integration
Handles user subscriptions and news delivery
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode, ChatAction
from sqlalchemy.orm import Session
from src.storage.database import SessionLocal, Subscriber, Article
from datetime import datetime
from config.settings import settings
from typing import List, Dict
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
        
        # Callback handler for inline buttons (Read More)
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
    
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
                    "✅ Highly relevant AI news\n"
                    "✅ Daily Digests (New!)\n"
                    "✅ 100% Free & Ad-free\n\n"
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
            "This bot delivers verified AI news from trusted sources.\n\n"
            "*Features:*\n"
            "• Instant alerts for major AI news\n"
            "• Daily Digest of top stories (New!)\n"
            "• Click 'Read More' for details\n"
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
                    f"Subscribed since: {subscriber.subscribed_at.strftime('%Y-%m-%d %H:%M UTC')}"
                )
            elif subscriber:
                status_text = (
                    f"❌ *Subscription Inactive*\n"
                )
            else:
                status_text = (
                    "📭 *Not Subscribed*\n"
                )
            
            await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            print(f"❌ Error in status_command: {e}")
            await update.message.reply_text("⚠️ Error checking status. Please try again.")
        finally:
            db.close()
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        await query.answer()  # Acknowledge click
        
        data = query.data
        if data.startswith("read_"):
            # Format: read_{article_id}
            article_id = int(data.split("_")[1])
            await self.send_article_detail(query.message.chat_id, article_id)
    
    async def send_article_detail(self, chat_id: int, article_id: int):
        """Send full details for a requested article"""
        db = SessionLocal()
        try:
            article = db.query(Article).filter(Article.id == article_id).first()
            if not article:
                await self.application.bot.send_message(chat_id, "⚠️ Article not found.")
                return

            message = (
                f"📰 *{article.title}*\n\n"
                f"{article.summary}\n\n"
                f"*Source:* {article.source_name}\n"
                f"[{article.source_domain}]({article.url})"
            )
            
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
            
        except Exception as e:
            print(f"❌ Error sending detail: {e}")
        finally:
            db.close()

    async def send_daily_digest(self, digest: Dict, article_map: Dict[int, int] = None) -> int:
        """
        Send daily digest to all subscribers
        
        Args:
            digest: JSON object with intro, items, outro
            article_map: Mapping of digest item index (if needed) to DB article ID
                         Actually, let's assume digest['items'] contains 'id' matching DB id.
                         
        Returns:
            Number of successful sends
        """
        db = SessionLocal()
        try:
            subscribers = db.query(Subscriber).filter(Subscriber.is_active == True).all()
            
            if not subscribers:
                return 0
            
            # Construct message
            message = f"☕ *Daily AI News Digest*\n\n{digest.get('intro', '')}\n\n"
            
            keyboard = []
            
            for item in digest.get('items', []):
                # Add item text
                message += f"🔹 *{item.get('headline')}*\n{item.get('impact')}\n\n"
                
                # Add button
                # We use a short callback data: read_{id}
                # Ensure id exists
                if 'id' in item:
                    keyboard.append([InlineKeyboardButton(
                        f"Read: {item.get('headline')[:20]}...", 
                        callback_data=f"read_{item['id']}"
                    )])
            
            message += f"{digest.get('outro', '')}"
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            print(f"📤 Sending Daily Digest to {len(subscribers)} subscribers...")
            
            tasks = []
            for sub in subscribers:
                tasks.append(
                    self.application.bot.send_message(
                        chat_id=sub.chat_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=reply_markup
                    )
                )
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = 0
            for res in results:
                if not isinstance(res, Exception):
                    success_count += 1
                else:
                    print(f"❌ Send failed: {res}")
            
            print(f"✅ Digest sent to {success_count}/{len(subscribers)} subscribers")
            return success_count
            
        except Exception as e:
            print(f"❌ Error sending daily digest: {e}")
            return 0
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
