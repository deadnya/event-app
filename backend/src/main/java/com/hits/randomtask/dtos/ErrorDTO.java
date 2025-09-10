package com.hits.randomtask.dtos;

import java.util.List;

public record ErrorDTO(
        Integer statusCode,
        List<String> errors
) { }
