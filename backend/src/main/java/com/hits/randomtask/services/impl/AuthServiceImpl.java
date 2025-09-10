package com.hits.randomtask.services.impl;

import com.hits.randomtask.dtos.*;
import com.hits.randomtask.entities.Company;
import com.hits.randomtask.entities.FullName;
import com.hits.randomtask.entities.Role;
import com.hits.randomtask.entities.User;
import com.hits.randomtask.mappers.UserMapper;
import com.hits.randomtask.services.AuthService;
import com.hits.randomtask.services.UUIDService;
import com.hits.randomtask.services.UserService;
import com.hits.randomtask.shared.exceptions.custom.AuthException;
import com.hits.randomtask.shared.exceptions.custom.BadRequestException;
import com.hits.randomtask.shared.exceptions.custom.NotFoundException;
import com.hits.randomtask.shared.security.JwtTokenService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    @Value("${telegram.bot.token}")
    private String telegramBotToken;

    private final AuthenticationManager authenticationManager;
    private final JwtTokenService jwtTokenService;
    private final UserService userService;
    private final UUIDService uuidService;
    private final UserMapper userMapper;

    @Override
    public AuthResponseDTO login(LoginRequestDTO request) {
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.email(), request.password())
        );

        User user = userService.findByEmail(request.email());
        return issueTokens(user);
    }

    @Override
    public AuthResponseDTO refresh(RefreshRequestDTO request) {

        String username = jwtTokenService.extractUsername(request.refreshToken());
        User user = userService.findByEmail(username);

        if (!jwtTokenService.isValidRefreshToken(request.refreshToken(), user)) {
            throw new AuthException("Invalid refresh token");
        }

        return issueAccessToken(user);
    }

    @Override
    public AuthResponseDTO loginWithTelegram(TelegramLoginRequestDTO request) {
        if (!verifyTelegramAuthData(request)) {
            throw new AuthException("Invalid Telegram authentication data");
        }

        User user = userService.findByTelegramId(request.id());

        if (user == null) {
            throw new AuthException("User not found. Please register via Telegram bot first.");
        }

        if (!user.getIsApproved()) {
            throw new AuthException("Account not approved by admin yet");
        }

        return issueTokens(user);
    }

    @Override
    public UserDTO registerTelegramUser(TelegramRegistrationDTO registrationDTO) {
        return userMapper.toDTO(userService.registerTelegramUser(registrationDTO));
    }

    private boolean verifyTelegramAuthData(TelegramLoginRequestDTO request) {
        try {
            Map<String, String> authData = new TreeMap<>();
            authData.put("auth_date", request.authDate().toString());
            authData.put("first_name", request.firstName());
            authData.put("id", request.id().toString());
            if (request.lastName() != null) {
                authData.put("last_name", request.lastName());
            }
            if (request.username() != null) {
                authData.put("username", request.username());
            }

            StringBuilder dataCheckString = new StringBuilder();
            authData.entrySet().stream()
                    .filter(entry -> !entry.getKey().equals("hash"))
                    .forEach(entry -> {
                        if (!dataCheckString.isEmpty()) {
                            dataCheckString.append("\n");
                        }
                        dataCheckString.append(entry.getKey()).append("=").append(entry.getValue());
                    });

            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKey = new SecretKeySpec(
                    telegramBotToken.getBytes(StandardCharsets.UTF_8),
                    "HmacSHA256"
            );
            mac.init(secretKey);
            byte[] hashBytes = mac.doFinal(dataCheckString.toString().getBytes(StandardCharsets.UTF_8));

            StringBuilder hexString = new StringBuilder();
            for (byte b : hashBytes) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }

            return hexString.toString().equals(request.hash());

        } catch (NoSuchAlgorithmException | InvalidKeyException e) {
            throw new AuthException("Error verifying Telegram authentication");
        }
    }

    private AuthResponseDTO issueTokens(User user) {
        String accessToken = jwtTokenService.generateAccessToken(user);
        String refreshToken = jwtTokenService.generateRefreshToken(user);
        jwtTokenService.saveToken(user, accessToken, refreshToken);

        return new AuthResponseDTO(
                accessToken,
                refreshToken
        );
    }

    private AuthResponseDTO issueAccessToken(User user) {
        String accessToken = jwtTokenService.generateAccessToken(user);

        return new AuthResponseDTO(
                accessToken,
                null
        );
    }
}