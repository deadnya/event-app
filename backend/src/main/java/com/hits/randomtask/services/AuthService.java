package com.hits.randomtask.services;

import com.hits.randomtask.dtos.*;
import com.hits.randomtask.entities.User;

public interface AuthService {
    AuthResponseDTO login(LoginRequestDTO request);
    AuthResponseDTO refresh(RefreshRequestDTO request);
    AuthResponseDTO loginWithTelegram(TelegramLoginRequestDTO request);
    UserDTO registerTelegramUser(TelegramRegistrationDTO registrationDTO);
}
