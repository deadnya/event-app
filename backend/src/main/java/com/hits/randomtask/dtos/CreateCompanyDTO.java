package com.hits.randomtask.dtos;

import jakarta.annotation.Nullable;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record CreateCompanyDTO(
        @Size(max = 255, message = "Max company name size = 255")
        @NotNull(message = "Company name is required")
        String name
) {
}
