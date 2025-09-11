package com.hits.randomtask.controllers;

import com.hits.randomtask.entities.User;
import com.hits.randomtask.services.GoogleCalendarService;
import com.hits.randomtask.shared.exceptions.custom.BadRequestException;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/google-calendar")
@RequiredArgsConstructor
@CrossOrigin
public class GoogleCalendarController {

    private final GoogleCalendarService googleCalendarService;

    @GetMapping("/auth-url")
    public ResponseEntity<Map<String, String>> getAuthorizationUrl(@AuthenticationPrincipal User user) {
        try {
            String authUrl = googleCalendarService.getAuthorizationUrl(user);
            return ResponseEntity.ok(Map.of("authUrl", authUrl));
        } catch (BadRequestException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/callback")
    public ResponseEntity<Map<String, String>> handleCallback(
            @RequestParam String code,
            @RequestParam(required = false) String state,
            @AuthenticationPrincipal User user) {
        
        googleCalendarService.handleCallback(code, user);
        return ResponseEntity.ok(Map.of("message", "Google Calendar connected successfully"));
    }

    @DeleteMapping("/disconnect")
    public ResponseEntity<Map<String, String>> disconnectGoogleCalendar(@AuthenticationPrincipal User user) {
        googleCalendarService.disconnectGoogleCalendar(user);
        return ResponseEntity.ok(Map.of("message", "Google Calendar disconnected successfully"));
    }

    @GetMapping("/status")
    public ResponseEntity<Map<String, Boolean>> getConnectionStatus(@AuthenticationPrincipal User user) {
        boolean isConnected = googleCalendarService.isGoogleCalendarConnected(user);
        return ResponseEntity.ok(Map.of("connected", isConnected));
    }
}
