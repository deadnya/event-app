from dataclasses import dataclass
from typing import Optional


@dataclass
class RegistrationData:
    telegram_chat_id: int
    telegram_username: str
    surname: str = ""
    name: str = ""
    patronymic: Optional[str] = None
    role: str = ""
    group: Optional[str] = None
    company_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        data = {
            'telegramChatId': self.telegram_chat_id,
            'telegramUsername': self.telegram_username,
            'surname': self.surname,
            'name': self.name,
            'role': self.role
        }
        
        if self.patronymic:
            data['patronymic'] = self.patronymic
        
        if self.role == 'STUDENT' and self.group:
            data['group'] = self.group
        elif self.role == 'MANAGER' and self.company_id:
            data['companyId'] = self.company_id
            
        return data
    
    def is_valid(self) -> bool:
        if not all([self.surname, self.name, self.role]):
            return False
        
        if self.role == 'STUDENT':
            return bool(self.group)
        elif self.role == 'MANAGER':
            return bool(self.company_id)
        
        return False
