from telegram import Update
from telegram.ext import ContextTypes
from .base_handler import BaseHandler
from ..config import STUDENT_ROLE
from ..utils.logger import logger


class StudentHandler(BaseHandler):
    async def student_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "student_help")
        
        user_id = update.effective_user.id
        user_role = await self.check_user_role(user_id)
        
        if user_role != STUDENT_ROLE:
            await update.message.reply_text("❌ This command is only available for students.")
            return
        
        if not await self.is_user_approved(user_id):
            await update.message.reply_text("❌ Your account is not approved yet.")
            return
        
        help_message = (
            "📚 Student Commands:\n\n"
            "/student_help - Show this help message\n"
            "/my_events - View your registered events\n"
            "/available_events - View available events to register\n"
            "/register_event - Register for an event\n"
            "/unregister_event - Unregister from an event"
        )
        await update.message.reply_text(help_message)
    
    async def my_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "my_events")
        
        user_id = update.effective_user.id
        user_role = await self.check_user_role(user_id)
        
        if user_role != STUDENT_ROLE:
            await update.message.reply_text("❌ This command is only available for students.")
            return
        
        if not await self.is_user_approved(user_id):
            await update.message.reply_text("❌ Your account is not approved yet.")
            return
        
        # TODO: Implement API call to get student's events
        await update.message.reply_text("🚧 This feature will be implemented soon!")
    
    async def available_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "available_events")
        
        user_id = update.effective_user.id
        user_role = await self.check_user_role(user_id)
        
        if user_role != STUDENT_ROLE:
            await update.message.reply_text("❌ This command is only available for students.")
            return
        
        if not await self.is_user_approved(user_id):
            await update.message.reply_text("❌ Your account is not approved yet.")
            return

        await update.message.reply_text("🚧 This feature will be implemented soon!")
    
    async def register_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "register_event")
        
        user_id = update.effective_user.id
        user_role = await self.check_user_role(user_id)
        
        if user_role != STUDENT_ROLE:
            await update.message.reply_text("❌ This command is only available for students.")
            return
        
        if not await self.is_user_approved(user_id):
            await update.message.reply_text("❌ Your account is not approved yet.")
            return
        
        # TODO: Implement event registration conversation
        await update.message.reply_text("🚧 This feature will be implemented soon!")
    
    async def unregister_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.log_command_usage(update, "unregister_event")
        
        user_id = update.effective_user.id
        user_role = await self.check_user_role(user_id)
        
        if user_role != STUDENT_ROLE:
            await update.message.reply_text("❌ This command is only available for students.")
            return
        
        if not await self.is_user_approved(user_id):
            await update.message.reply_text("❌ Your account is not approved yet.")
            return
        
        # TODO: Implement event unregistration conversation
        await update.message.reply_text("🚧 This feature will be implemented soon!")
