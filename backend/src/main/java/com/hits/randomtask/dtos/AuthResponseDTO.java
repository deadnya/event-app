package com.hits.randomtask.dtos;

public record AuthResponseDTO(
        String accessToken,
        String refreshToken
) { }
