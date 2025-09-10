package com.hits.randomtask.services;

import com.hits.randomtask.dtos.TelegramRegistrationDTO;
import com.hits.randomtask.entities.User;

public interface UserService {
    User findByEmail(String email);
    User findByID(String id);
    User findByTelegramId(Long telegramId);
    User registerTelegramUser(TelegramRegistrationDTO registrationDTO);
    User findByTelegramChatId(Long telegramChatId);
}