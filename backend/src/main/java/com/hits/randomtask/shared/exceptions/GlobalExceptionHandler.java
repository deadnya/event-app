package com.hits.randomtask.shared.exceptions;

import com.hits.randomtask.dtos.ErrorDTO;
import com.hits.randomtask.shared.exceptions.custom.BadRequestException;
import com.hits.randomtask.shared.exceptions.custom.ForbiddenException;
import com.hits.randomtask.shared.exceptions.custom.NotFoundException;
import jakarta.security.auth.message.AuthException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;

import java.util.ArrayList;
import java.util.List;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorDTO> handleMethodArgumentNotValidException(MethodArgumentNotValidException ex, WebRequest request) {

        List<String> errors = new ArrayList<>();
        ex.getBindingResult().getAllErrors().forEach(error -> {
            String name = ((FieldError) error).getField();
            String message = error.getDefaultMessage();
            errors.add(name + ": " + message);
        });

        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(new ErrorDTO(HttpStatus.BAD_REQUEST.value(), errors));
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ErrorDTO> handleHttpMessageNotReadableException(HttpMessageNotReadableException ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(new ErrorDTO(HttpStatus.BAD_REQUEST.value(), List.of("Invalid enum value")));
    }

    @ExceptionHandler(AuthException.class)
    public ResponseEntity<ErrorDTO> handleAuthException(AuthException ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.UNAUTHORIZED)
                .body(new ErrorDTO(HttpStatus.UNAUTHORIZED.value(), List.of(ex.getMessage())));
    }

    @ExceptionHandler(BadRequestException.class)
    public ResponseEntity<ErrorDTO> handleBadRequestException(BadRequestException ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(new ErrorDTO(HttpStatus.BAD_REQUEST.value(), List.of(ex.getMessage())));
    }

    @ExceptionHandler(NotFoundException.class)
    public ResponseEntity<ErrorDTO> handleNotFoundException(NotFoundException ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.NOT_FOUND)
                .body(new ErrorDTO(HttpStatus.NOT_FOUND.value(), List.of(ex.getMessage())));
    }

    @ExceptionHandler(ForbiddenException.class)
    public ResponseEntity<ErrorDTO> handleForbiddenException(ForbiddenException ex, WebRequest request) {
        return ResponseEntity
                .status(HttpStatus.FORBIDDEN)
                .body(new ErrorDTO(HttpStatus.FORBIDDEN.value(), List.of(ex.getMessage())));
    }
}
