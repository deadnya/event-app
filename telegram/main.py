import os
import logging
import asyncio
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/app/logs/bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://backend:8080/api')

SURNAME, NAME, PATRONYMIC, ROLE, GROUP_OR_COMPANY = range(5)

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
        self.registration_data = {}
    
    def setup_handlers(self):
        registration_handler = ConversationHandler(
            entry_points=[CommandHandler('register', self.start_registration)],
            states={
                SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_surname)],
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_name)],
                PATRONYMIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_patronymic)],
                ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_role)],
                GROUP_OR_COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_group_or_company)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel_registration)]
        )
        
        self.application.add_handler(registration_handler)
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.check_status))
        
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        try:
            response = requests.get(f"{API_BASE_URL}/users/telegram/{user_id}")
            if response.status_code == 200:
                try:
                    user_data = response.json()
                    if user_data.get('isApproved'):
                        message = "✅ You are already registered and approved! You can log in to the web application."
                    else:
                        message = "⏳ You are registered but waiting for admin approval."
                except (ValueError, AttributeError):
                    message = "⏳ You are registered but status is unclear. Please contact support."
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
        except requests.exceptions.RequestException:
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

    async def start_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        try:
            response = requests.get(f"{API_BASE_URL}/users/telegram/{user_id}")
            if response.status_code == 200:
                await update.message.reply_text(
                    "You are already registered! Use /status to check your approval status."
                )
                return ConversationHandler.END
        except requests.exceptions.RequestException:
            pass
        
        self.registration_data[user_id] = {
            'telegramChatId': user_id,
            'telegramUsername': update.effective_user.username or f"user_{user_id}"
        }
        
        await update.message.reply_text(
            "Let's register your account! 📝\n\n"
            "First, please enter your surname:"
        )
        return SURNAME

    async def get_surname(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self.registration_data[user_id]['surname'] = update.message.text.strip()
        
        await update.message.reply_text("Now, please enter your name:")
        return NAME

    async def get_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self.registration_data[user_id]['name'] = update.message.text.strip()
        
        await update.message.reply_text(
            "Please enter your patronymic (or type 'none' if you don't have one):"
        )
        return PATRONYMIC

    async def get_patronymic(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        patronymic = update.message.text.strip()
        
        if patronymic.lower() != 'none':
            self.registration_data[user_id]['patronymic'] = patronymic
        
        keyboard = [['STUDENT', 'MANAGER']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "Please select your role:",
            reply_markup=reply_markup
        )
        return ROLE

    async def get_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        role = update.message.text.strip().upper()
        
        if role not in ['STUDENT', 'MANAGER']:
            await update.message.reply_text(
                "Please select either STUDENT or MANAGER:",
                reply_markup=ReplyKeyboardMarkup([['STUDENT', 'MANAGER']], one_time_keyboard=True)
            )
            return ROLE
        
        self.registration_data[user_id]['role'] = role
        
        if role == 'STUDENT':
            await update.message.reply_text(
                "Please enter your group:",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            try:
                response = requests.get(f"{API_BASE_URL}/company/all")
                if response.status_code == 200:
                    try:
                        companies = response.json()
                        company_list = "\n".join([f"{c['id']} - {c['name']}" for c in companies])
                        await update.message.reply_text(
                            f"Available companies:\n{company_list}\n\n"
                            "Please enter the company ID:",
                            reply_markup=ReplyKeyboardRemove()
                        )
                    except (ValueError, AttributeError, KeyError):
                        await update.message.reply_text(
                            "Please enter your company ID:",
                            reply_markup=ReplyKeyboardRemove()
                        )
                else:
                    await update.message.reply_text(
                        "Please enter your company ID:",
                        reply_markup=ReplyKeyboardRemove()
                    )
            except requests.exceptions.RequestException:
                await update.message.reply_text(
                    "Please enter your company ID:",
                    reply_markup=ReplyKeyboardRemove()
                )
        
        return GROUP_OR_COMPANY

    async def get_group_or_company(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        value = update.message.text.strip()
        
        if self.registration_data[user_id]['role'] == 'STUDENT':
            self.registration_data[user_id]['group'] = value
        else:
            self.registration_data[user_id]['companyId'] = value
        
        try:
            # Debug: Log the data being sent
            logger.info(f"Sending registration data: {self.registration_data[user_id]}")
            
            response = requests.post(
                f"{API_BASE_URL}/auth/register-telegram",
                json=self.registration_data[user_id],
                headers={'Content-Type': 'application/json'}
            )
            
            logger.info(f"Registration response status: {response.status_code}")
            logger.info(f"Registration response headers: {response.headers}")
            logger.info(f"Registration response text: {response.text}")
            
            if response.status_code == 200:
                await update.message.reply_text(
                    "✅ Registration successful!\n\n"
                    "Your account has been submitted for admin approval. "
                    "You will be notified once approved and can then log in to the web application."
                )
            else:
                # Handle non-200 responses more carefully
                try:
                    error_message = response.json().get('message', 'Unknown error')
                except (ValueError, AttributeError):
                    # If response is not JSON or doesn't have message field
                    error_message = f"HTTP {response.status_code}: {response.text[:100] if response.text else 'No response body'}"
                
                await update.message.reply_text(
                    f"❌ Registration failed: {error_message}\n"
                    "Please try again with /register"
                )
                logger.error(f"Registration failed with status {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            await update.message.reply_text(
                "❌ Registration failed due to connection error. Please try again later."
            )
            logger.error(f"Registration API connection error: {e}")
        except Exception as e:
            await update.message.reply_text(
                "❌ Registration failed due to an unexpected error. Please try again later."
            )
            logger.error(f"Registration unexpected error: {e}")
        
        if user_id in self.registration_data:
            del self.registration_data[user_id]
        
        return ConversationHandler.END

    async def cancel_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id in self.registration_data:
            del self.registration_data[user_id]
        
        await update.message.reply_text(
            "Registration cancelled. Use /register to start over.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    async def check_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        try:
            response = requests.get(f"{API_BASE_URL}/users/telegram/{user_id}")
            if response.status_code == 200:
                try:
                    user_data = response.json()
                    if user_data.get('isApproved'):
                        await update.message.reply_text("✅ Your account is approved! You can log in to the web application.")
                    else:
                        await update.message.reply_text("⏳ Your account is pending admin approval.")
                except (ValueError, AttributeError):
                    await update.message.reply_text("⏳ Your account status is unclear. Please contact support.")
            else:
                await update.message.reply_text("❌ You are not registered. Use /register to create an account.")
        except requests.exceptions.RequestException:
            await update.message.reply_text("❌ Unable to check status. Please try again later.")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_message = (
            "📋 Available Commands:\n\n"
            "/start - Welcome message\n"
            "/help - Show this help message\n"
            "/status - Check backend system status\n\n"
            "💬 You can also send regular messages for general interaction!"
        )
        await update.message.reply_text(help_message)
        logger.info(f"Help command used by user {update.effective_user.id}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                await update.message.reply_text("✅ Backend system is healthy and running!")
            else:
                await update.message.reply_text(f"⚠️ Backend system returned status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            await update.message.reply_text("❌ Backend system is not responding.")
            logger.error(f"Backend health check failed: {e}")
        
        logger.info(f"Status command used by user {update.effective_user.id}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        user_message = update.message.text
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        logger.info(f"Message from {username} (ID: {user_id}): {user_message}")
        
        # Here you can add logic to process the message and interact with your backend
        # For example:
        try:
            # Example API call to backend
            # response = requests.post(f"{API_BASE_URL}/process-message", 
            #                         json={"message": user_message, "user_id": user_id})
            
            # For now, just echo the message
            response_message = f"Thanks for your message: '{user_message}'\n\nI received it and logged it!"
            await update.message.reply_text(response_message)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text("Sorry, I encountered an error processing your message.")
            
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Update {update} caused error {context.error}")
    
    def run(self):
        logger.info("Starting Telegram Bot...")
        
        self.application.add_error_handler(self.error_handler)

        self.application.run_polling()

def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set!")
        return
    
    logger.info("Initializing Telegram Bot...")
    bot = TelegramBot()
    bot.run()

if __name__ == '__main__':
    main()
