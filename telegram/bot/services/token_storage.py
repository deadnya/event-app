import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ..utils.logger import logger


class TokenStorage:
    def __init__(self, storage_file: str = None):
        if storage_file is None:
            import os
            if os.path.exists("/app"):
                storage_file = "/app/data/user_tokens.json"
            else:
                storage_file = "data/user_tokens.json"
        
        self.storage_file = storage_file
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
    
    def _load_tokens(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            return {}
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading tokens: {e}")
            return {}
    
    def _save_tokens(self, tokens: Dict[str, Any]):
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(tokens, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving tokens: {e}")
    
    def store_user_tokens(self, telegram_id: int, access_token: str, refresh_token: str):
        tokens = self._load_tokens()
        tokens[str(telegram_id)] = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'stored_at': datetime.now().isoformat()
        }
        self._save_tokens(tokens)
        logger.info(f"Tokens stored for user {telegram_id}")
    
    def get_user_tokens(self, telegram_id: int) -> Optional[Dict[str, str]]:
        tokens = self._load_tokens()
        user_tokens = tokens.get(str(telegram_id))
        if user_tokens:
            return {
                'access_token': user_tokens['access_token'],
                'refresh_token': user_tokens['refresh_token']
            }
        return None
    
    def remove_user_tokens(self, telegram_id: int):
        tokens = self._load_tokens()
        if str(telegram_id) in tokens:
            del tokens[str(telegram_id)]
            self._save_tokens(tokens)
            logger.info(f"Tokens removed for user {telegram_id}")
    
    def clear_all_tokens(self):
        self._save_tokens({})
        logger.info("All tokens cleared")
