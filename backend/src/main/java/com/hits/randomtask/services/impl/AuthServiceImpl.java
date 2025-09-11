package com.hits.randomtask.services.impl;

import com.hits.randomtask.dtos.*;
import com.hits.randomtask.entities.User;
import com.hits.randomtask.mappers.UserMapper;
import com.hits.randomtask.services.AuthService;
import com.hits.randomtask.services.UUIDService;
import com.hits.randomtask.services.UserService;
import com.hits.randomtask.shared.exceptions.custom.AuthException;
import com.hits.randomtask.shared.exceptions.custom.NotFoundException;
import com.hits.randomtask.shared.security.JwtTokenService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Map;
import java.util.TreeMap;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private static final Logger logger = LoggerFactory.getLogger(AuthServiceImpl.class);

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
        logger.info("Refreshing token for user identifier: {}", username);

        User user = null;
        try {
            user = userService.findByEmail(username);
            logger.info("Found user by email: {}", username);
        } catch (NotFoundException e) {
            try {
                Long telegramId = Long.parseLong(username);
                user = userService.findByTelegramId(telegramId);
                if (user == null) {
                    logger.warn("User not found with Telegram ID: {}", telegramId);
                    throw new AuthException("User not found with identifier: " + username);
                }
                logger.info("Found user by Telegram ID: {}", telegramId);
            } catch (NumberFormatException nfe) {
                logger.warn("Invalid identifier format: {}", username);
                throw new AuthException("User not found with identifier: " + username);
            }
        }

        if (!jwtTokenService.isValidRefreshToken(request.refreshToken(), user)) {
            throw new AuthException("Invalid refresh token");
        }

        return issueAccessToken(user);
    }

    @Override
    public AuthResponseDTO loginWithTelegram(TelegramLoginRequestDTO request) {
        logger.info("Starting Telegram login for user ID: {}", request.id());
        
        if (!verifyTelegramAuthData(request)) {
            logger.warn("Telegram authentication verification failed for user ID: {}", request.id());
            throw new AuthException("Invalid Telegram authentication data");
        }
        
        logger.info("Telegram authentication verification passed for user ID: {}", request.id());

        User user = userService.findByTelegramId(request.id());

        if (user == null) {
            logger.warn("User not found for Telegram ID: {}", request.id());
            throw new AuthException("User not found. Please register via Telegram bot first.");
        }
        
        logger.info("Found user: {} (ID: {})", user.getName().getFullName(), user.getId());

        if (!user.getIsApproved()) {
            logger.warn("User not approved: {} (Telegram ID: {})", user.getName().getFullName(), request.id());
            throw new AuthException("Account not approved by admin yet");
        }
        
        logger.info("User is approved, issuing tokens for: {}", user.getName().getFullName());

        return issueTokens(user);
    }

    @Override
    public UserDTO registerTelegramUser(TelegramRegistrationDTO registrationDTO) {
        return userMapper.toDTO(userService.registerTelegramUser(registrationDTO));
    }

    private boolean verifyTelegramAuthData(TelegramLoginRequestDTO request) {
        try {
            logger.info("Verifying Telegram auth data for user ID: {}", request.id());
            logger.info("Request hash: {}", request.hash());
            logger.info("Auth date: {}", request.authDate());
            logger.info("Using bot token starting with: {}...", telegramBotToken.substring(0, Math.min(10, telegramBotToken.length())));
            
            long currentTime = System.currentTimeMillis() / 1000;
            long authTime = request.authDate();
            logger.info("Time check - Current: {}, Auth: {}, Diff: {} seconds", 
                       currentTime, authTime, currentTime - authTime);
            
            if (currentTime - authTime > 86400) {
                logger.warn("Auth date is too old. Current: {}, Auth: {}, Diff: {} seconds", 
                            currentTime, authTime, currentTime - authTime);
                return false;
            }
            
            Map<String, String> authData = new TreeMap<>();
            authData.put("auth_date", request.authDate().toString());
            authData.put("first_name", request.firstName());
            authData.put("id", request.id().toString());
            if (request.lastName() != null && !request.lastName().isEmpty()) {
                authData.put("last_name", request.lastName());
            }
            if (request.username() != null && !request.username().isEmpty()) {
                authData.put("username", request.username());
            }

            StringBuilder dataCheckString = new StringBuilder();
            
            Map<String, String> sortedData = new TreeMap<>(authData);
            boolean first = true;
            for (Map.Entry<String, String> entry : sortedData.entrySet()) {
                if (!first) {
                    dataCheckString.append("\n");
                }
                dataCheckString.append(entry.getKey()).append("=").append(entry.getValue());
                first = false;
            }

            logger.info("Data check string: {}", dataCheckString.toString());

            MessageDigest sha256 = MessageDigest.getInstance("SHA-256");
            byte[] secretKeyBytes = sha256.digest(telegramBotToken.getBytes(StandardCharsets.UTF_8));

            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKey = new SecretKeySpec(secretKeyBytes, "HmacSHA256");
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

            String computedHash = hexString.toString();
            logger.info("Computed hash: {}", computedHash);
            logger.info("Expected hash: {}", request.hash());
            boolean isValid = computedHash.equals(request.hash());
            logger.info("Hash verification result: {}", isValid);

            return isValid;

        } catch (NoSuchAlgorithmException | InvalidKeyException e) {
            logger.error("Error verifying Telegram authentication", e);
            throw new AuthException("Error verifying Telegram authentication");
        }
    }

    @Transactional
    private AuthResponseDTO issueTokens(User user) {
        logger.info("Issuing new tokens for user: {} (Telegram ID: {})", user.getName().getFullName(), user.getTelegramChatId());

        logger.info("Revoking all existing tokens for user: {}", user.getName().getFullName());
        jwtTokenService.revokeAllTokens(user);
        
        String accessToken = jwtTokenService.generateAccessToken(user);
        String refreshToken = jwtTokenService.generateRefreshToken(user);
        jwtTokenService.saveToken(user, accessToken, refreshToken);
        logger.info("Tokens saved successfully for user: {}", user.getName().getFullName());

        return new AuthResponseDTO(
                accessToken,
                refreshToken
        );
    }

    @Transactional
    private AuthResponseDTO issueAccessToken(User user) {
        logger.info("Refreshing tokens for user: {} (Telegram ID: {})", user.getName().getFullName(), user.getTelegramChatId());

        logger.info("Revoking all existing tokens for user: {}", user.getName().getFullName());
        jwtTokenService.revokeAllTokens(user);

        String accessToken = jwtTokenService.generateAccessToken(user);
        String refreshToken = jwtTokenService.generateRefreshToken(user);
        jwtTokenService.saveToken(user, accessToken, refreshToken);
        logger.info("New tokens saved successfully for user: {}", user.getName().getFullName());

        return new AuthResponseDTO(
                accessToken,
                refreshToken
        );
    }
}