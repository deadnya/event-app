import requests
from typing import Dict, Any, Optional, Tuple
from ..config import API_BASE_URL
from ..utils.logger import logger
from .token_storage import TokenStorage
from .jwt_service import JWTTokenService


class AuthService:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token_storage = TokenStorage()
        self.jwt_service = JWTTokenService()
    
    def telegram_login(self, telegram_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, str]]]:
        try:
            logger.debug(f"Attempting Telegram login for user {telegram_data.get('id')}")
            logger.debug(f"Auth data: {telegram_data}")
            
            response = requests.post(
                f"{self.base_url}/auth/telegram-login",
                json=telegram_data,
                headers={'Content-Type': 'application/json'}
            )
            
            logger.debug(f"Backend response status: {response.status_code}")
            
            if response.status_code == 200:
                auth_response = response.json()
                tokens = {
                    'access_token': auth_response['accessToken'],
                    'refresh_token': auth_response.get('refreshToken')
                }
                
                telegram_id = telegram_data.get('id')
                if telegram_id and tokens['refresh_token']:
                    self.token_storage.store_user_tokens(
                        telegram_id, 
                        tokens['access_token'], 
                        tokens['refresh_token']
                    )
                
                return True, "Login successful", tokens
            else:
                error_msg = "Login failed"
                try:
                    error_response = response.json()
                    error_msg = error_response.get('message', error_msg)
                    logger.error(f"Backend login error: {error_response}")
                except Exception as e:
                    logger.error(f"Failed to parse error response: {e}")
                    logger.error(f"Raw response: {response.text}")
                return False, error_msg, None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Telegram login error: {e}")
            return False, "Connection error during login", None
        except Exception as e:
            logger.error(f"Unexpected login error: {e}")
            return False, "Unexpected error during login", None
    
    def refresh_access_token(self, telegram_id: int) -> Tuple[bool, str, Optional[str]]:
        try:
            stored_tokens = self.token_storage.get_user_tokens(telegram_id)
            if not stored_tokens or not stored_tokens.get('refresh_token'):
                return False, "No refresh token available", None
            
            response = requests.post(
                f"{self.base_url}/auth/refresh",
                json={'refreshToken': stored_tokens['refresh_token']},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                auth_response = response.json()
                new_access_token = auth_response['accessToken']
                
                self.token_storage.store_user_tokens(
                    telegram_id,
                    new_access_token,
                    stored_tokens['refresh_token']
                )
                
                return True, "Token refreshed successfully", new_access_token
            else:
                self.token_storage.remove_user_tokens(telegram_id)
                return False, "Refresh token expired, please login again", None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Token refresh error: {e}")
            return False, "Connection error during token refresh", None
        except Exception as e:
            logger.error(f"Unexpected refresh error: {e}")
            return False, "Unexpected error during token refresh", None
    
    def logout_user(self, telegram_id: int):
        self.token_storage.remove_user_tokens(telegram_id)
        logger.info(f"User {telegram_id} logged out")
    
    def get_valid_access_token(self, telegram_id: int) -> Optional[str]:
        stored_tokens = self.token_storage.get_user_tokens(telegram_id)
        if not stored_tokens:
            logger.debug(f"No stored tokens for user {telegram_id}")
            return None
        
        access_token = stored_tokens['access_token']
        
        is_expired = self.jwt_service.is_token_expired(access_token)
        logger.debug(f"Token expired check for user {telegram_id}: {is_expired}")
        
        if is_expired:
            logger.info(f"Access token expired for user {telegram_id}, attempting refresh")
            success, _, new_token = self.refresh_access_token(telegram_id)
            if success and new_token:
                logger.info(f"Token refresh successful for user {telegram_id}")
                return new_token
            else:
                logger.info(f"Token refresh failed for user {telegram_id}")
                return None
        
        return access_token
    
    def is_user_logged_in(self, telegram_id: int) -> bool:
        return self.get_valid_access_token(telegram_id) is not None
    
    def get_user_info_from_token(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        access_token = self.get_valid_access_token(telegram_id)
        if not access_token:
            return None
        
        return self.jwt_service.get_token_user_info(access_token)
