package com.hits.randomtask.shared.exceptions.custom;

public class ForbiddenException extends RuntimeException {
    public ForbiddenException(String message) {
        super(message);
    }
}
