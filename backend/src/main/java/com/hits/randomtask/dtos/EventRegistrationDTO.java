package com.hits.randomtask.dtos;

import java.time.LocalDateTime;

public record EventRegistrationDTO(
        Long id,
        UserDTO user,
        LocalDateTime registeredAt,
        String googleEventId
) { }
