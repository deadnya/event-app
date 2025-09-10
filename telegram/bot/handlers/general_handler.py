from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from .base_handler import BaseHandler
from ..utils.logger import logger


class GeneralHandler(BaseHandler):
    def get_role_keyboard(self, role):
        if role == "STUDENT":
            keyboard = [
                [KeyboardButton("/my_events"), KeyboardButton("/find_events")],
                [KeyboardButton("/available_events"), KeyboardButton("/student_help")]
            ]
        elif role == "MANAGER":
            keyboard = [
                [KeyboardButton("/my_company_events"), KeyboardButton("/create_event")],
                [KeyboardButton("/event_stats"), KeyboardButton("/manager_help")]
            ]
        else:
            keyboard = [
                [KeyboardButton("/register"), KeyboardButton("/help")],
                [KeyboardButton("/status"), KeyboardButton("/backend_health")]
            ]
        
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "start")
        
        user_id = update.effective_user.id
        
        if await self.auto_authenticate_user(update):
            user_role = await self.check_user_role(user_id)
            keyboard = self.get_role_keyboard(user_role)
            message = (
                f"✅ Welcome back!\n\n"
                f"🏷️ Role: {user_role}\n"
                f"You're logged in and ready to use all features.\n\n"
                f"Use the buttons below for quick access to your commands!"
            )
        else:
            user_data = self.api_service.get_user_by_telegram_id(user_id)
            if user_data:
                if user_data.get('isApproved'):
                    keyboard = self.get_role_keyboard(None)
                    message = "❌ Authentication failed. Please contact support."
                else:
                    keyboard = self.get_role_keyboard(None)
                    message = "⏳ You are registered but waiting for admin approval."
            else:
                keyboard = self.get_role_keyboard(None)
                message = (
                    "🚀 Welcome to HITS Task Bot!\n\n"
                    "To access the system, you need to register your account.\n"
                    "Use the 📝 Register button or /register command.\n\n"
                    "Use the buttons below for quick access!"
                )
        
        await update.message.reply_text(message, reply_markup=keyboard)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "help")
        
        user_id = update.effective_user.id
        
        await self.auto_authenticate_user(update)
        is_authenticated = await self.is_user_authenticated(user_id)
        
        help_message = (
            "📋 <b>Available Commands:</b>\n\n"
            "<b>General Commands:</b>\n"
            "/start - Welcome message and role keyboard\n"
            "/help - Show this help message\n"
            "/status - Check your registration status\n"
            "/register - Register your account\n"
            "/backend_health - Check backend system health\n\n"
        )
        
        if is_authenticated:
            user_role = await self.check_user_role(user_id)
            keyboard = self.get_role_keyboard(user_role)
            
            if user_role == "STUDENT":
                help_message += (
                    "<b>Student Commands:</b>\n"
                    "📚 My Events - View your registered events\n"
                    "🔍 Find Events - Search for events\n"
                    "📅 Available Events - View all available events\n"
                    "❓ Student Help - Student-specific help\n\n"
                    "You can also use:\n"
                    "/register_event &lt;event_id&gt; - Register for an event\n"
                    "/unregister_event &lt;event_id&gt; - Unregister from an event\n\n"
                )
            elif user_role == "MANAGER":
                help_message += (
                    "<b>Manager Commands:</b>\n"
                    "🏢 Company Events - View your company's events\n"
                    "➕ Create Event - Create a new event\n"
                    "📊 Event Stats - View event statistics\n"
                    "❓ Manager Help - Manager-specific help\n\n"
                    "You can also use:\n"
                    "/edit_event - Edit an existing event\n"
                    "/delete_event - Delete an event\n\n"
                )
        else:
            keyboard = self.get_role_keyboard(None)
            user_data = self.api_service.get_user_by_telegram_id(user_id)
            if not user_data:
                help_message += (
                    "<b>Quick Actions:</b>\n"
                    "📝 Register - Create your account\n"
                    "❓ Help - Show this help\n"
                    "📋 Status - Check your status\n"
                    "🏥 Backend Health - System status\n\n"
                    "<b>Next Steps:</b>\n"
                    "📝 Use the Register button to create your account and access more features!\n\n"
                )
            elif not user_data.get('isApproved'):
                help_message += (
                    "<b>Status:</b>\n"
                    "⏳ Your account is pending admin approval. More commands will be available after approval.\n\n"
                )
        
        help_message += "💬 You can also send regular messages for general interaction!"
        await update.message.reply_text(help_message, parse_mode='HTML', reply_markup=keyboard)
    
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
        logger.debug(f"Unhandled message from {username}: {user_message}")
