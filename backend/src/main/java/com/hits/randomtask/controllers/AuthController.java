package com.hits.randomtask.controllers;

import com.hits.randomtask.dtos.*;
import com.hits.randomtask.services.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public ResponseEntity<AuthResponseDTO> login(@Valid @RequestBody LoginRequestDTO loginRequestDTO) {
        return ResponseEntity.ok(authService.login(loginRequestDTO));
    }

    @PostMapping("/refresh")
    public ResponseEntity<AuthResponseDTO> authRefreshPost(@Valid @RequestBody RefreshRequestDTO refreshRequestDTO) {
        return ResponseEntity.ok(authService.refresh(refreshRequestDTO));
    }

    @PostMapping("/telegram-login")
    public ResponseEntity<AuthResponseDTO> loginWithTelegram(@Valid @RequestBody TelegramLoginRequestDTO request) {
        return ResponseEntity.ok(authService.loginWithTelegram(request));
    }

    @PostMapping("/register-telegram")
    public ResponseEntity<String> registerTelegramUser(@Valid @RequestBody TelegramRegistrationDTO registrationDTO) {
        authService.registerTelegramUser(registrationDTO);
        return ResponseEntity.ok("Registration successful. Waiting for admin approval.");
    }
}