import base64
import json
from datetime import datetime
from typing import Dict, Any, Optional
from ..utils.logger import logger


class JWTTokenService:
    @staticmethod
    def decode_jwt_payload(token: str) -> Optional[Dict[str, Any]]:
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            payload = parts[1]
            padding = len(payload) % 4
            if padding:
                payload += '=' * (4 - padding)
            
            decoded_bytes = base64.urlsafe_b64decode(payload)
            return json.loads(decoded_bytes)
        
        except Exception as e:
            logger.error(f"Error decoding JWT payload: {e}")
            return None
    
    @staticmethod
    def is_token_expired(token: str, buffer_seconds: int = 60) -> bool:
        try:
            payload = JWTTokenService.decode_jwt_payload(token)
            if not payload or 'exp' not in payload:
                return True
            
            exp_timestamp = payload['exp']
            current_timestamp = datetime.now().timestamp()
            
            logger.debug(f"Token exp: {exp_timestamp}, current: {current_timestamp}, diff: {exp_timestamp - current_timestamp}")
            
            return (exp_timestamp - buffer_seconds) <= current_timestamp
        
        except Exception as e:
            logger.error(f"Error checking token expiry: {e}")
            return True
    
    @staticmethod
    def get_token_user_info(token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = JWTTokenService.decode_jwt_payload(token)
            if not payload:
                return None
            
            return {
                'user_id': payload.get('sub'),
                'email': payload.get('email'),
                'role': payload.get('role'),
                'telegram_id': payload.get('telegramId'),
                'exp': payload.get('exp'),
                'iat': payload.get('iat')
            }
        
        except Exception as e:
            logger.error(f"Error extracting user info from token: {e}")
            return None
