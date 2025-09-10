import requests
from typing import Dict, Any, Optional
from ..config import API_BASE_URL
from ..utils.logger import logger


class APIService:
    
    def __init__(self):
        self.base_url = API_BASE_URL
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(f"{self.base_url}/users/telegram/{telegram_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching user by telegram ID {telegram_id}: {e}")
            return None
    
    def register_telegram_user(self, registration_data: Dict[str, Any]) -> tuple[bool, str]:
        try:
            logger.info(f"Sending registration data: {registration_data}")
            
            response = requests.post(
                f"{self.base_url}/auth/register-telegram",
                json=registration_data,
                headers={'Content-Type': 'application/json'}
            )
            
            logger.info(f"Registration response status: {response.status_code}")
            logger.info(f"Registration response text: {response.text}")
            
            if response.status_code == 200:
                return True, "Registration successful"
            else:
                try:
                    error_message = response.json().get('message', 'Unknown error')
                except (ValueError, AttributeError):
                    error_message = f"HTTP {response.status_code}: {response.text[:100] if response.text else 'No response body'}"
                
                logger.error(f"Registration failed with status {response.status_code}: {response.text}")
                return False, error_message
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Registration API connection error: {e}")
            return False, "Connection error. Please try again later."
        except Exception as e:
            logger.error(f"Registration unexpected error: {e}")
            return False, "Unexpected error. Please try again later."
    
    def get_companies(self) -> Optional[list]:
        try:
            response = requests.get(f"{self.base_url}/company/all")
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching companies: {e}")
            return None
    
    def check_backend_health(self) -> tuple[bool, str]:
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return True, "Backend system is healthy and running!"
            else:
                return False, f"Backend system returned status code: {response.status_code}"
        except requests.exceptions.RequestException as e:
            logger.error(f"Backend health check failed: {e}")
            return False, "Backend system is not responding."
