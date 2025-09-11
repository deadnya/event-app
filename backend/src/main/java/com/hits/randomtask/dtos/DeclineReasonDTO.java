package com.hits.randomtask.dtos;

import jakarta.annotation.Nullable;
import jakarta.validation.constraints.Size;

public record DeclineReasonDTO(
        @Size(max = 255, message = "Reason must be at most 255 characters long")
        @Nullable
        String reason
) {
}
