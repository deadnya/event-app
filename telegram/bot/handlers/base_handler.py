from telegram import Update
from telegram.ext import ContextTypes
from ..services.api_service import APIService
from ..utils.logger import logger


class BaseHandler:
    def __init__(self):
        self.api_service = APIService()
        
    async def check_user_role(self, user_id: int) -> str:
        user_data = self.api_service.get_user_by_telegram_id(user_id)
        if user_data:
            return user_data.get('role', 'UNKNOWN')
        return 'UNREGISTERED'
    
    async def is_user_approved(self, user_id: int) -> bool:
        user_data = self.api_service.get_user_by_telegram_id(user_id)
        if user_data:
            return user_data.get('isApproved', False)
        return False
    
    async def log_command_usage(self, update: Update, command_name: str):
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        logger.info(f"{command_name} command used by {username} (ID: {user_id})")
