from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from .base_handler import BaseHandler
from ..config import SURNAME, NAME, PATRONYMIC, ROLE, GROUP_OR_COMPANY, AVAILABLE_ROLES, STUDENT_ROLE, MANAGER_ROLE, COMPANIES_PER_PAGE
from ..models.registration import RegistrationData
from ..utils.logger import logger
import math


class RegistrationHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.registration_data = {}
        self.company_pages = {}
    
    def _create_company_keyboard(self, companies, page=0):
        if not companies:
            return None
            
        total_pages = math.ceil(len(companies) / COMPANIES_PER_PAGE)
        
        page = max(0, min(page, total_pages - 1))
        
        start_idx = page * COMPANIES_PER_PAGE
        end_idx = min(start_idx + COMPANIES_PER_PAGE, len(companies))
        
        keyboard = []
        
        for i in range(start_idx, end_idx):
            company = companies[i]
            button_number = i - start_idx + 1
            company_name = company.get('name', 'Unknown Company')
            display_name = company_name[:30] + '...' if len(company_name) > 30 else company_name
            keyboard.append([
                InlineKeyboardButton(
                    f"{button_number}. {display_name}", 
                    callback_data=f"company_{company['id']}"
                )
            ])
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{page-1}"))
        
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)

        if total_pages > 1:
            keyboard.append([InlineKeyboardButton(f"Page {page + 1}/{total_pages}", callback_data="noop")])
        
        return InlineKeyboardMarkup(keyboard)
    
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
        else:
            companies = self.api_service.get_companies()
            if companies and len(companies) > 0:
                self.company_pages[user_id] = companies
                
                keyboard = self._create_company_keyboard(companies, page=0)
                await update.message.reply_text(
                    "<b>📢 Please select your company:</b>\n\n"
                    "Click on the number corresponding to your company from the list below:",
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    "❌ Unable to load companies. Please contact support.",
                    reply_markup=ReplyKeyboardRemove()
                )
                self._cleanup_registration_data(user_id)
                return ConversationHandler.END
        
        return GROUP_OR_COMPANY
    
    async def handle_company_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        if user_id not in self.registration_data:
            await query.edit_message_text("❌ Registration session expired. Please start over with /register")
            return ConversationHandler.END
        
        if user_id not in self.company_pages:
            await query.edit_message_text("❌ Company data not found. Please start over with /register")
            self._cleanup_registration_data(user_id)
            return ConversationHandler.END
        
        companies = self.company_pages[user_id]
        
        if query.data.startswith("page_"):
            try:
                page = int(query.data.split("_")[1])
                keyboard = self._create_company_keyboard(companies, page=page)
                await query.edit_message_text(
                    "<b>📢 Please select your company:</b>\n\n"
                    "Click on the number corresponding to your company from the list below:",
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            except (ValueError, IndexError):
                await query.edit_message_text("❌ Invalid page. Please start over with /register")
                self._cleanup_registration_data(user_id)
                return ConversationHandler.END
            
            return GROUP_OR_COMPANY
        
        elif query.data.startswith("company_"):
            try:
                company_id = query.data.split("_", 1)[1]
                
                selected_company = next((c for c in companies if c['id'] == company_id), None)
                if not selected_company:
                    await query.edit_message_text("❌ Invalid company selection. Please start over with /register")
                    self._cleanup_registration_data(user_id)
                    return ConversationHandler.END
                
                self.registration_data[user_id].company_id = company_id
                
                await query.edit_message_text(
                    f"✅ <b>Selected Company:</b> {selected_company['name']}\n\n"
                    "Processing your registration...",
                    parse_mode='HTML'
                )
                
                return await self._complete_registration(update, context, user_id, query)
                
            except (ValueError, IndexError):
                await query.edit_message_text("❌ Invalid company selection. Please start over with /register")
                self._cleanup_registration_data(user_id)
                return ConversationHandler.END
        
        elif query.data == "noop":
            return GROUP_OR_COMPANY
        
        return GROUP_OR_COMPANY
    
    async def _complete_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, query=None):
        registration_data = self.registration_data[user_id]
        
        if not registration_data.is_valid():
            message = "❌ Registration data is incomplete. Please try again with /register"
            if query:
                await query.edit_message_text(message)
            else:
                await update.message.reply_text(message)
            self._cleanup_registration_data(user_id)
            return ConversationHandler.END
        
        success, message = self.api_service.register_telegram_user(registration_data.to_dict())
        
        if success:
            response_message = (
                "✅ <b>Registration successful!</b>\n\n"
                "Your account has been submitted for admin approval. "
                "You will be notified once approved and can then log in to the web application."
            )
        else:
            response_message = (
                f"❌ <b>Registration failed:</b> {message}\n"
                "Please try again with /register"
            )
        
        if query:
            await query.edit_message_text(response_message, parse_mode='HTML')
        else:
            await update.message.reply_text(response_message, parse_mode='HTML')
        
        self._cleanup_registration_data(user_id)
        return ConversationHandler.END
    
    async def get_group_or_company(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if user_id not in self.registration_data:
            await update.message.reply_text(
                "❌ Registration session expired. Please start over with /register"
            )
            return ConversationHandler.END
        
        registration_data = self.registration_data[user_id]
        
        if registration_data.role == STUDENT_ROLE:
            value = update.message.text.strip()
            registration_data.group = value
            
            return await self._complete_registration(update, context, user_id)
        else:
            await update.message.reply_text(
                "Please use the buttons above to select your company."
            )
            return GROUP_OR_COMPANY
    
    async def cancel_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self._cleanup_registration_data(user_id)
        
        await update.message.reply_text(
            "Registration cancelled. Use /register to start over.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    def _cleanup_registration_data(self, user_id: int):
        if user_id in self.registration_data:
            del self.registration_data[user_id]
        if user_id in self.company_pages:
            del self.company_pages[user_id]
