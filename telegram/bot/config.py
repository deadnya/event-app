import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://backend:8080/api')

SURNAME, NAME, PATRONYMIC, ROLE, GROUP_OR_COMPANY = range(5)

STUDENT_ROLE = 'STUDENT'
MANAGER_ROLE = 'MANAGER'
ADMIN_ROLE = 'ADMIN'

AVAILABLE_ROLES = [STUDENT_ROLE, MANAGER_ROLE]
