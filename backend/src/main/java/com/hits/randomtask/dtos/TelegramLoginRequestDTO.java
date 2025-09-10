package com.hits.randomtask.dtos;

import jakarta.validation.constraints.NotNull;

public record TelegramLoginRequestDTO(
        @NotNull Long id,
        @NotNull String firstName,
        String lastName,
        String username,
        @NotNull Long authDate,
        @NotNull String hash
) {}