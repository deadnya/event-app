package com.hits.randomtask.dtos;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record TelegramRegistrationDTO(
        @NotNull Long telegramChatId,
        @NotBlank String telegramUsername,
        @NotBlank String surname,
        @NotBlank String name,
        String patronymic,
        @NotBlank String role,
        String group,
        String companyId
) {}
