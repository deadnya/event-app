package com.hits.randomtask.dtos;

import com.hits.randomtask.validators.ValidEventDates;
import jakarta.annotation.Nullable;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.time.LocalDateTime;

@ValidEventDates
public record EditEventDTO(

        @NotNull(message = "Event id must be present")
        String id,

        @Size(max = 255, message = "Max event name size = 255")
        @NotEmpty(message = "Event name must not be empty")
        String name,

        @Size(max = 3000, message = "Max event description size = 3000")
        @Nullable
        String description,

        @NotNull
        LocalDateTime date,

        @NotNull
        LocalDateTime registrationDeadline,

        @NotEmpty(message = "Event location must not be empty")
        String location
) {
}
