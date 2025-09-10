from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from .base_handler import BaseHandler
from ..config import SURNAME, NAME, PATRONYMIC, ROLE, GROUP_OR_COMPANY, AVAILABLE_ROLES, STUDENT_ROLE, MANAGER_ROLE
from ..models.registration import RegistrationData
from ..utils.logger import logger


class RegistrationHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.registration_data = {}
    
    async def start_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "register")
        
        user_id = update.effective_user.id
        
        user_data = self.api_service.get_user_by_telegram_id(user_id)
        if user_data:
            await update.message.reply_text(
                "You are already registered! Use /status to check your approval status."
            )
            return ConversationHandler.END
        
        self.registration_data[user_id] = RegistrationData(
            telegram_chat_id=user_id,
            telegram_username=update.effective_user.username or f"user_{user_id}"
        )
        
        await update.message.reply_text(
            "Let's register your account! 📝\n\n"
            "First, please enter your surname:"
        )
        return SURNAME
    
    async def get_surname(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self.registration_data[user_id].surname = update.message.text.strip()
        
        await update.message.reply_text("Now, please enter your name:")
        return NAME
    
    async def get_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self.registration_data[user_id].name = update.message.text.strip()
        
        await update.message.reply_text(
            "Please enter your patronymic (or type 'none' if you don't have one):"
        )
        return PATRONYMIC
    
    async def get_patronymic(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        patronymic = update.message.text.strip()
        
        if patronymic.lower() != 'none':
            self.registration_data[user_id].patronymic = patronymic
        
        keyboard = [[role for role in AVAILABLE_ROLES]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "Please select your role:",
            reply_markup=reply_markup
        )
        return ROLE
    
    async def get_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        role = update.message.text.strip().upper()
        
        if role not in AVAILABLE_ROLES:
            keyboard = [[role for role in AVAILABLE_ROLES]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(
                f"Please select one of: {', '.join(AVAILABLE_ROLES)}:",
                reply_markup=reply_markup
            )
            return ROLE
        
        self.registration_data[user_id].role = role
        
        if role == STUDENT_ROLE:
            await update.message.reply_text(
                "Please enter your group:",
                reply_markup=ReplyKeyboardRemove()
            )
        else:  # MANAGER_ROLE
            companies = self.api_service.get_companies()
            if companies:
                try:
                    company_list = "\n".join([f"{c['id']} - {c['name']}" for c in companies])
                    await update.message.reply_text(
                        f"Available companies:\n{company_list}\n\n"
                        "Please enter the company ID:",
                        reply_markup=ReplyKeyboardRemove()
                    )
                except (KeyError, TypeError):
                    await update.message.reply_text(
                        "Please enter your company ID:",
                        reply_markup=ReplyKeyboardRemove()
                    )
            else:
                await update.message.reply_text(
                    "Please enter your company ID:",
                    reply_markup=ReplyKeyboardRemove()
                )
        
        return GROUP_OR_COMPANY
    
    async def get_group_or_company(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        value = update.message.text.strip()
        
        registration_data = self.registration_data[user_id]
        
        if registration_data.role == STUDENT_ROLE:
            registration_data.group = value
        else:  # MANAGER_ROLE
            registration_data.company_id = value
        
        if not registration_data.is_valid():
            await update.message.reply_text(
                "❌ Registration data is incomplete. Please try again with /register"
            )
            self._cleanup_registration_data(user_id)
            return ConversationHandler.END
        
        success, message = self.api_service.register_telegram_user(registration_data.to_dict())
        
        if success:
            await update.message.reply_text(
                "✅ Registration successful!\n\n"
                "Your account has been submitted for admin approval. "
                "You will be notified once approved and can then log in to the web application."
            )
        else:
            await update.message.reply_text(
                f"❌ Registration failed: {message}\n"
                "Please try again with /register"
            )
        
        self._cleanup_registration_data(user_id)
        return ConversationHandler.END
    
    async def cancel_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the registration process"""
        user_id = update.effective_user.id
        self._cleanup_registration_data(user_id)
        
        await update.message.reply_text(
            "Registration cancelled. Use /register to start over.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    def _cleanup_registration_data(self, user_id: int):
        """Clean up registration data for user"""
        if user_id in self.registration_data:
            del self.registration_data[user_id]
