import hashlib
import hmac
import time
from telegram import Update
from telegram.ext import ContextTypes
from .base_handler import BaseHandler
from ..config import BOT_TOKEN
from ..utils.logger import logger


class LoginHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.bot_token_hash = self._get_bot_token_hash()
    
    def _get_bot_token_hash(self) -> str:
        return hashlib.sha256(BOT_TOKEN.encode()).hexdigest()
    
    def _create_telegram_auth_data(self, user) -> dict:
        auth_date = int(time.time())
        
        data_check_arr = [
            f"auth_date={auth_date}",
            f"first_name={user.first_name or ''}",
            f"id={user.id}"
        ]
        
        if user.last_name:
            data_check_arr.append(f"last_name={user.last_name}")
        
        if user.username:
            data_check_arr.append(f"username={user.username}")
        
        data_check_arr.sort()
        data_check_string = '\n'.join(data_check_arr)
        
        secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
        hash_value = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        return {
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username or "",
            "auth_date": auth_date,
            "hash": hash_value
        }
    
    async def login_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "login")
        
        user_id = update.effective_user.id
        
        if self.api_service.auth_service.is_user_logged_in(user_id):
            await update.message.reply_text("✅ You are already logged in!")
            return
        
        user_data = self.api_service.get_user_by_telegram_id(user_id)
        if not user_data:
            await update.message.reply_text(
                "❌ You are not registered. Please use /register first."
            )
            return
        
        if not user_data.get('isApproved'):
            await update.message.reply_text(
                "❌ Your account is not approved yet. Please wait for admin approval."
            )
            return
        
        auth_data = self._create_telegram_auth_data(update.effective_user)
        
        success, message, tokens = self.api_service.auth_service.telegram_login(auth_data)
        
        if success:
            user_info = self.api_service.auth_service.get_user_info_from_token(user_id)
            role = user_info.get('role', 'Unknown') if user_info else 'Unknown'
            
            await update.message.reply_text(
                f"✅ Login successful!\n"
                f"Role: {role}\n"
                f"Welcome back! You can now use role-specific commands."
            )
        else:
            await update.message.reply_text(f"❌ Login failed: {message}")
    
    async def logout_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "logout")
        
        user_id = update.effective_user.id
        
        if not self.api_service.auth_service.is_user_logged_in(user_id):
            await update.message.reply_text("❌ You are not logged in.")
            return
        
        self.api_service.auth_service.logout_user(user_id)
        
        await update.message.reply_text(
            "✅ Logged out successfully!\n"
            "Use /login to log in again and access role-specific commands."
        )
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "profile")
        
        user_id = update.effective_user.id
        
        if not self.api_service.auth_service.is_user_logged_in(user_id):
            await update.message.reply_text(
                "❌ You need to login first. Use /login command."
            )
            return
        
        user_info = self.api_service.auth_service.get_user_info_from_token(user_id)
        
        if user_info:
            profile_text = (
                "👤 <b>Your Profile</b>\n\n"
                f"📧 Email: {user_info.get('email', 'N/A')}\n"
                f"🏷️ Role: {user_info.get('role', 'N/A')}\n"
                f"🆔 User ID: {user_info.get('user_id', 'N/A')}\n"
                f"📱 Telegram ID: {user_info.get('telegram_id', 'N/A')}"
            )
        else:
            profile_text = "❌ Unable to fetch profile information."
        
        await update.message.reply_text(profile_text, parse_mode='HTML')
