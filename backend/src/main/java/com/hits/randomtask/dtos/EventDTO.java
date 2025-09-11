package com.hits.randomtask.dtos;

import java.time.LocalDateTime;
import java.util.List;

public record EventDTO(
        String id,
        String name,
        String description,
        String location,
        LocalDateTime date,
        LocalDateTime registrationDeadline,
        List<EventRegistrationDTO> registrations
) { }
