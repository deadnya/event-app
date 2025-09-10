from telegram import Update
from telegram.ext import ContextTypes
from .base_handler import BaseHandler
from ..utils.logger import logger


class GeneralHandler(BaseHandler):
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "start")
        
        user_id = update.effective_user.id
        user_data = self.api_service.get_user_by_telegram_id(user_id)
        
        if user_data:
            if user_data.get('isApproved'):
                message = "✅ You are already registered and approved! You can log in to the web application."
            else:
                message = "⏳ You are registered but waiting for admin approval."
        else:
            message = (
                "🚀 Welcome to HITS Task Bot!\n\n"
                "To access the system, you need to register your account.\n"
                "Use /register to start the registration process.\n\n"
                "Available commands:\n"
                "/register - Start registration\n"
                "/help - Show available commands\n"
                "/status - Check your registration status"
            )
        
        await update.message.reply_text(message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "help")
        
        help_message = (
            "📋 Available Commands:\n\n"
            "/start - Welcome message\n"
            "/help - Show this help message\n"
            "/status - Check your registration status\n"
            "/register - Register your account\n\n"
            "💬 You can also send regular messages for general interaction!"
        )
        await update.message.reply_text(help_message)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "status")
        
        user_id = update.effective_user.id
        user_data = self.api_service.get_user_by_telegram_id(user_id)
        
        if user_data:
            if user_data.get('isApproved'):
                await update.message.reply_text("✅ Your account is approved! You can log in to the web application.")
            else:
                await update.message.reply_text("⏳ Your account is pending admin approval.")
        else:
            await update.message.reply_text("❌ You are not registered. Use /register to create an account.")
    
    async def backend_health_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "backend_health")
        
        is_healthy, message = self.api_service.check_backend_health()
        status_emoji = "✅" if is_healthy else "❌"
        await update.message.reply_text(f"{status_emoji} {message}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_message = update.message.text
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        logger.info(f"Message from {username} (ID: {user_id}): {user_message}")
        
        try:
            response_message = f"Thanks for your message: '{user_message}'\n\nI received it and logged it!"
            await update.message.reply_text(response_message)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text("Sorry, I encountered an error processing your message.")
