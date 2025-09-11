import requests
from typing import Dict, Any, Optional
from ..config import API_BASE_URL
from ..utils.logger import logger
from .auth_service import AuthService


class APIService:
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.auth_service = AuthService()
    
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
    
    def _get_auth_headers(self, telegram_id: int) -> Optional[Dict[str, str]]:
        access_token = self.auth_service.get_valid_access_token(telegram_id)
        if not access_token:
            logger.error(f"No access token available for user {telegram_id}")
            return None
        
        logger.debug(f"Got access token for user {telegram_id}: {access_token[:20]}...")
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_authenticated_request(self, method: str, endpoint: str, telegram_id: int, **kwargs) -> Optional[requests.Response]:
        headers = self._get_auth_headers(telegram_id)
        if not headers:
            logger.error(f"No valid token for user {telegram_id}")
            return None
        
        try:
            if 'headers' in kwargs:
                kwargs['headers'].update(headers)
            else:
                kwargs['headers'] = headers
            
            url = f"{self.base_url}/{endpoint}"
            logger.info(f"Making {method} request to {url} for user {telegram_id}")
            logger.info(f"Request headers: {dict(kwargs.get('headers', {}))}")
            logger.info(f"Request payload: {kwargs.get('json', 'No JSON payload')}")
            
            response = requests.request(method, url, timeout=30, **kwargs)
            logger.info(f"Response received - Status: {response.status_code}")
            
            if response.status_code == 401:
                logger.warning(f"Authentication failed for user {telegram_id}, clearing stored tokens")
                self.auth_service.logout_user(telegram_id)
                if response.status_code >= 400:
                    logger.error(f"Error response body: {response.text}")
                return response
            
            if response.status_code >= 400:
                logger.error(f"Error response body: {response.text}")
            
            return response
        except requests.exceptions.ConnectionError as e:
            logger.error(f"CONNECTION ERROR to {self.base_url}/{endpoint}: {str(e)}")
            logger.error(f"Full error details: {repr(e)}")
            return None
        except requests.exceptions.Timeout as e:
            logger.error(f"TIMEOUT ERROR for {endpoint}: {str(e)}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"REQUEST EXCEPTION for {endpoint}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            return None
        except Exception as e:
            logger.error(f"UNEXPECTED ERROR for {endpoint}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            return None
    
    def get_student_events(self, telegram_id: int) -> Optional[list]:
        logger.info(f"Fetching registered events for student {telegram_id}")
        response = self._make_authenticated_request('GET', 'student/events', telegram_id)
        if response and response.status_code == 200:
            events = response.json()
            logger.info(f"Retrieved {len(events)} registered events for student {telegram_id}")
            return events
        logger.warning(f"Failed to get registered events for student {telegram_id}")
        return None

    def get_all_events(self, telegram_id: int) -> Optional[list]:
        logger.info(f"Fetching all events for student {telegram_id}")
        response = self._make_authenticated_request('GET', 'student/event', telegram_id)
        if response and response.status_code == 200:
            events = response.json()
            logger.info(f"Retrieved {len(events)} total events for student {telegram_id}")
            return events
        logger.warning(f"Failed to get all events for student {telegram_id}")
        return None
        return None
    
    def register_for_event(self, telegram_id: int, event_id: str) -> tuple[bool, str]:
        response = self._make_authenticated_request(
            'POST', 
            f'student/event/{event_id}/register', 
            telegram_id
        )
        
        if response:
            if response.status_code == 200:
                return True, "Successfully registered for event"
            else:
                try:
                    error_msg = response.json().get('message', 'Registration failed')
                except:
                    error_msg = f"Registration failed with status {response.status_code}"
                return False, error_msg
        
        return False, "Connection error during registration"
    
    def unregister_from_event(self, telegram_id: int, event_id: str) -> tuple[bool, str]:
        response = self._make_authenticated_request(
            'DELETE', 
            f'student/event/{event_id}/unregister', 
            telegram_id
        )
        
        if response:
            if response.status_code == 200:
                return True, "Successfully unregistered from event"
            else:
                try:
                    error_msg = response.json().get('message', 'Unregistration failed')
                except:
                    error_msg = f"Unregistration failed with status {response.status_code}"
                return False, error_msg
        
        return False, "Connection error during unregistration"
    
    def get_company_events(self, telegram_id: int) -> Optional[list]:
        response = self._make_authenticated_request('GET', 'manager/events', telegram_id)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def create_event(self, telegram_id: int, event_data: Dict[str, Any]) -> tuple[bool, str]:

        logger.info(f"Creating event for telegram_id {telegram_id} with data: {event_data}")
        logger.info(f"API Base URL: {self.base_url}")
        
        headers = self._get_auth_headers(telegram_id)
        if not headers:
            logger.error(f"No valid token for user {telegram_id} when creating event")
            return False, "Authentication error. Please login again with /start"
        
        response = self._make_authenticated_request(
            'POST', 
            'manager/event/create', 
            telegram_id,
            json=event_data
        )
        
        if response:
            logger.info(f"Event creation response status: {response.status_code}")
            logger.info(f"Event creation response body: {response.text}")
            
            if response.status_code in [200, 201]:
                return True, "Event created successfully"
            elif response.status_code == 401:
                logger.error(f"Authentication failed (401): {response.text}")
                return False, "Authentication failed. Please login again with /start"
            else:
                try:
                    error_msg = response.json().get('message', 'Event creation failed')
                except:
                    error_msg = f"Event creation failed with status {response.status_code}: {response.text[:200]}"
                logger.error(f"Event creation failed: {error_msg}")
                return False, error_msg
        
        logger.error(f"No response received for event creation for user {telegram_id}")
        return False, "Connection error during event creation"

    def edit_event(self, telegram_id: int, event_data: Dict[str, Any]) -> tuple[bool, str]:
        logger.info(f"Editing event for telegram_id {telegram_id} with data: {event_data}")
        logger.info(f"API Base URL: {self.base_url}")
        
        headers = self._get_auth_headers(telegram_id)
        if not headers:
            logger.error(f"No valid token for user {telegram_id} when editing event")
            return False, "Authentication error. Please login again with /start"
        
        response = self._make_authenticated_request(
            'PUT', 
            'manager/event/edit', 
            telegram_id,
            json=event_data
        )
        
        if response:
            logger.info(f"Event edit response status: {response.status_code}")
            logger.info(f"Event edit response body: {response.text}")
            
            if response.status_code in [200, 201]:
                return True, "Event updated successfully"
            elif response.status_code == 401:
                logger.error(f"Authentication failed (401): {response.text}")
                return False, "Authentication failed. Please login again with /start"
            else:
                try:
                    error_msg = response.json().get('message', 'Event edit failed')
                except:
                    error_msg = f"Event edit failed with status {response.status_code}: {response.text[:200]}"
                logger.error(f"Event edit failed: {error_msg}")
                return False, error_msg
        
        logger.error(f"No response received for event edit for user {telegram_id}")
        return False, "Connection error during event edit"

    def get_event_by_id(self, telegram_id: int, event_id: str) -> Optional[Dict[str, Any]]:
        response = self._make_authenticated_request('GET', f'manager/event/{event_id}', telegram_id)
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def get_event_participants(self, telegram_id: int, event_id: str) -> Optional[list]:
        response = self._make_authenticated_request('GET', f'manager/event/{event_id}', telegram_id)
        if response and response.status_code == 200:
            event_data = response.json()
            return event_data.get('registrations', [])
        return None
    
    def delete_event(self, telegram_id: int, event_id: str) -> tuple[bool, str]:
        response = self._make_authenticated_request('DELETE', f'manager/event/{event_id}', telegram_id)
        
        if response:
            if response.status_code == 200:
                return True, "Event deleted successfully"
            else:
                try:
                    error_msg = response.json().get('message', 'Event deletion failed')
                except:
                    error_msg = f"Event deletion failed with status {response.status_code}"
                return False, error_msg
        
        return False, "Connection error during event deletion"

    def get_pending_users(self, telegram_id: int) -> Optional[list]:
        response = self._make_authenticated_request('GET', 'manager/users/pending', telegram_id)
        
        if response:
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get pending users: {response.status_code} - {response.text}")
                return None
        
        logger.error(f"No response received for pending users request for user {telegram_id}")
        return None

    def approve_user(self, telegram_id: int, user_id: str) -> tuple[bool, str]:
        response = self._make_authenticated_request('PATCH', f'manager/approve-user/{user_id}', telegram_id)
        
        if response:
            if response.status_code == 200:
                return True, "User approved successfully"
            else:
                try:
                    error_msg = response.json().get('message', 'User approval failed')
                except:
                    error_msg = f"User approval failed with status {response.status_code}"
                logger.error(f"User approval failed: {error_msg}")
                return False, error_msg
        
        logger.error(f"No response received for user approval for user {telegram_id}")
        return False, "Connection error during user approval"

    def decline_user(self, telegram_id: int, user_id: str, reason: Optional[str] = None) -> tuple[bool, str]:
        decline_data = {"reason": reason} if reason else {"reason": None}
        
        response = self._make_authenticated_request(
            'PATCH', 
            f'manager/decline-user/{user_id}', 
            telegram_id,
            json=decline_data
        )
        
        if response:
            if response.status_code == 200:
                return True, "User declined successfully"
            else:
                try:
                    error_msg = response.json().get('message', 'User decline failed')
                except:
                    error_msg = f"User decline failed with status {response.status_code}"
                logger.error(f"User decline failed: {error_msg}")
                return False, error_msg
        
        logger.error(f"No response received for user decline for user {telegram_id}")
        return False, "Connection error during user decline"
