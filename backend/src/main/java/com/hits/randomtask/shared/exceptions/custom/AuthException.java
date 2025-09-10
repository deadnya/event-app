package com.hits.randomtask.shared.exceptions.custom;

public class AuthException extends RuntimeException {
    public AuthException(String message) {
        super(message);
    }
}