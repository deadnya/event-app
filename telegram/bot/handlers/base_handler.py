from telegram import Update
from telegram.ext import ContextTypes
from ..services.api_service import APIService
from ..utils.logger import logger


class BaseHandler:
    def __init__(self):
        self.api_service = APIService()
        
    async def check_user_role(self, user_id: int) -> str:
        logger.debug(f"Checking role for user {user_id}")

        if self.api_service.auth_service.is_user_logged_in(user_id):
            logger.debug(f"User {user_id} is logged in, getting role from token")
            user_info = self.api_service.auth_service.get_user_info_from_token(user_id)
            if user_info:
                role = user_info.get('role', 'UNKNOWN')
                logger.debug(f"Role from token for user {user_id}: {role}")
                return role
        
        logger.debug(f"User {user_id} not logged in, fetching from API")
        user_data = self.api_service.get_user_by_telegram_id(user_id)
        if user_data:
            role = user_data.get('role', 'UNKNOWN')
            logger.debug(f"Role from API for user {user_id}: {role}")
            logger.debug(f"Full user data: {user_data}")
            return role
        
        logger.debug(f"User {user_id} not found, returning UNREGISTERED")
        return 'UNREGISTERED'
    
    async def is_user_approved(self, user_id: int) -> bool:
        user_data = self.api_service.get_user_by_telegram_id(user_id)
        if user_data:
            return user_data.get('isApproved', False)
        return False
    
    async def is_user_authenticated(self, user_id: int) -> bool:
        return self.api_service.auth_service.is_user_logged_in(user_id)
    
    async def require_authentication(self, update: Update) -> bool:
        user_id = update.effective_user.id
        
        if not await self.is_user_authenticated(user_id):
            await update.message.reply_text(
                "🔐 You are not logged in. Please use /start to authenticate.",
                parse_mode='HTML'
            )
            return False
        
        user_role = await self.check_user_role(user_id)
        if user_role == 'UNREGISTERED':
            self.api_service.auth_service.logout_user(user_id)
            await update.message.reply_text(
                "🚫 <b>Authentication Error</b>\n\n"
                "Your account is no longer valid. This could happen if:\n"
                "• Your account was deleted by an administrator\n"
                "• Your registration was revoked\n\n"
                "Please use /start to register again.",
                parse_mode='HTML'
            )
            return False
        
        return True
    
    
    async def auto_authenticate_user(self, update: Update) -> bool:
        user_id = update.effective_user.id
        
        if await self.is_user_authenticated(user_id):
            user_info = self.api_service.auth_service.get_user_info_from_token(user_id)
            if user_info and user_info.get('role') is not None:
                logger.debug(f"User {user_id} already authenticated with valid role")
                return True
            else:
                logger.info(f"Clearing old token without role info for user {user_id}")
                self.api_service.auth_service.token_storage.remove_user_tokens(user_id)
        
        user_data = self.api_service.get_user_by_telegram_id(user_id)
        if not user_data:
            return False
        
        if not user_data.get('isApproved'):
            return False

        auth_data = self._create_telegram_auth_data(update.effective_user)
        success, message, tokens = self.api_service.auth_service.telegram_login(auth_data)
        
        if success:
            logger.info(f"Auto-authenticated user {user_id}")
            return True
        else:
            logger.error(f"Auto-authentication failed for user {user_id}: {message}")
            return False
    
    def _create_telegram_auth_data(self, user) -> dict:
        import hashlib
        import hmac
        import time
        from ..config import BOT_TOKEN
        
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
        
        logger.debug(f"Auth data string for user {user.id}: {data_check_string}")
        
        secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
        hash_value = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        auth_data = {
            "id": user.id,
            "firstName": user.first_name or "",
            "lastName": user.last_name or "",
            "username": user.username or "",
            "authDate": auth_date,
            "hash": hash_value
        }
        
        logger.debug(f"Generated auth data: {auth_data}")
        
        return auth_data
    
    async def require_authentication(self, update: Update) -> bool:
        user_id = update.effective_user.id
        
        logger.debug(f"Requiring authentication for user {user_id}")

        if await self.auto_authenticate_user(update):
            logger.debug(f"Auto-authentication successful for user {user_id}")
            return True
        
        logger.debug(f"Auto-authentication failed for user {user_id}, checking reason")
        
        user_data = self.api_service.get_user_by_telegram_id(user_id)
        if not user_data:
            logger.debug(f"User {user_id} not found in database")
            await update.message.reply_text(
                "❌ You need to register first.\n"
                "Use /register to create your account."
            )
        elif not user_data.get('isApproved'):
            logger.debug(f"User {user_id} not approved: {user_data.get('isApproved')}")
            await update.message.reply_text(
                "⏳ Your account is pending admin approval.\n"
                "Please wait for approval before using this feature."
            )
        else:
            logger.debug(f"User {user_id} registered and approved but authentication still failed")
            await update.message.reply_text(
                "❌ Authentication failed. Please contact support if this persists."
            )
        
        return False
    
    async def require_role(self, update: Update, required_role: str) -> bool:
        user_id = update.effective_user.id
        
        logger.debug(f"Checking role for user {user_id}, required: {required_role}")
        
        if not await self.require_authentication(update):
            logger.debug(f"User {user_id} failed authentication check")
            return False
        
        user_role = await self.check_user_role(user_id)
        logger.debug(f"User {user_id} has role: {user_role}")
        
        if user_role != required_role:
            logger.warning(f"Role mismatch for user {user_id}: has '{user_role}', needs '{required_role}'")
            await update.message.reply_text(
                f"❌ This command is only available for {required_role.lower()}s."
            )
            return False
        
        logger.debug(f"Role check passed for user {user_id}")
        return True
    
    async def log_command_usage(self, update: Update, command_name: str):
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        logger.info(f"{command_name} command used by {username} (ID: {user_id})")
