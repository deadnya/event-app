package com.hits.randomtask.shared.security;

import com.hits.randomtask.entities.Token;
import com.hits.randomtask.entities.User;
import com.hits.randomtask.repositories.TokenRepository;
import com.hits.randomtask.services.UUIDService;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.time.Instant;
import java.util.Date;
import java.util.List;
import java.util.function.Function;

@Component
@RequiredArgsConstructor
public class JwtTokenService {

    private static final Logger logger = LoggerFactory.getLogger(JwtTokenService.class);

    @Value("${jwt.secret}")
    private String jwtSecret;

    @Value("${jwt.access-expiration-ms}")
    private long accessExpirationMs;

    @Value("${jwt.refresh-expiration-ms}")
    private long refreshExpirationMs;

    private final TokenRepository tokenRepository;
    private final UUIDService uuidService;

    public String generateAccessToken(User user) {
        return generateToken(user, accessExpirationMs);
    }

    public String generateRefreshToken(User user) {
        return generateToken(user, refreshExpirationMs );
    }

    private String generateToken(User user, long expireTime) {
        String primaryRole = user.getRoles().stream()
                .findFirst()
                .map(role -> role.getRole().name())
                .orElse("UNKNOWN");
        
        String subject = user.getEmail() != null ? user.getEmail() : String.valueOf(user.getTelegramChatId());
        
        return Jwts
                .builder()
                .subject(subject)
                .claim("role", primaryRole)
                .claim("telegramId", user.getTelegramChatId())
                .claim("userId", user.getId())
                .id(uuidService.getRandomUUID())
                .issuedAt(new Date(System.currentTimeMillis()))
                .expiration(new Date(System.currentTimeMillis() + expireTime ))
                .signWith(getSigningKey())
                .compact();
    }

    public String extractUsername(String token) {
        if (token == null || token.trim().isEmpty()) {
            logger.warn("Attempted to extract username from null or empty token");
            return null;
        }
        return extractClaim(token, Claims::getSubject);
    }

    public <T> T extractClaim(String token, Function<Claims, T> resolver) {
        if (token == null || token.trim().isEmpty()) {
            logger.warn("Attempted to extract claim from null or empty token");
            return null;
        }
        Claims claims = extractAllClaims(token);
        return resolver.apply(claims);
    }

    private Claims extractAllClaims(String token) {
        if (token == null || token.trim().isEmpty()) {
            logger.warn("Attempted to extract claims from null or empty token");
            throw new IllegalArgumentException("Token cannot be null or empty");
        }
        return Jwts
                .parser()
                .verifyWith(getSigningKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    public boolean isValid(String token, UserDetails user) {
        if (token == null || token.trim().isEmpty()) {
            logger.warn("Token validation failed: token is null or empty");
            return false;
        }
        
        String username = extractUsername(token);
        if (username == null) {
            logger.warn("Token validation failed: unable to extract username");
            return false;
        }
        
        logger.info("Validating token for user: {}", username);

        boolean validToken = tokenRepository
                .findByAccessToken(token)
                .map(t -> {
                    logger.info("Token found in DB with ID: {}, loggedOut: {}, token starts with: {}...", 
                               t.getId(), t.isLoggedOut(), 
                               t.getAccessToken().substring(0, Math.min(20, t.getAccessToken().length())));
                    return !t.isLoggedOut();
                })
                .orElse(false);

        boolean expired = isTokenExpired(token);
        logger.info("Token expired: {}", expired);
        logger.info("Username matches: {}", username.equals(user.getUsername()));
        logger.info("Token valid in DB: {}", validToken);

        boolean result = (username.equals(user.getUsername())) && !expired && validToken;
        logger.info("Final validation result: {}", result);
        
        return result;
    }

    public boolean isValidRefreshToken(String token, User user) {
        if (token == null || token.trim().isEmpty()) {
            logger.warn("Refresh token validation failed: token is null or empty");
            return false;
        }
        
        String username = extractUsername(token);
        if (username == null) {
            logger.warn("Refresh token validation failed: unable to extract username");
            return false;
        }

        logger.info("Validating refresh token - extracted username: '{}', user.getUsername(): '{}'", username, user.getUsername());

        boolean validRefreshToken = tokenRepository
                .findByRefreshToken(token)
                .map(t -> {
                    logger.info("Refresh token found in DB with ID: {}, loggedOut: {}, refresh token starts with: {}...", 
                               t.getId(), t.isLoggedOut(), 
                               t.getRefreshToken().substring(0, Math.min(20, t.getRefreshToken().length())));
                    return !t.isLoggedOut();
                })
                .orElse(false);

        logger.info("Refresh token DB validation: {}", validRefreshToken);
        
        boolean expired = isTokenExpired(token);
        logger.info("Refresh token expired: {}", expired);
        
        boolean usernameMatches = username.equals(user.getUsername());
        logger.info("Username matches: {}", usernameMatches);

        boolean result = usernameMatches && !expired && validRefreshToken;
        logger.info("Final refresh token validation result: {}", result);
        
        return result;
    }

    private boolean isTokenExpired(String token) {
        if (token == null || token.trim().isEmpty()) {
            logger.warn("Token expiration check failed: token is null or empty");
            return true;
        }
        
        Date expiration = extractExpiration(token);
        if (expiration == null) {
            logger.warn("Token expiration check failed: unable to extract expiration date");
            return true;
        }
        
        Date now = new Date();
        boolean expired = expiration.before(now);
        logger.info("Token expiration check - expires at: {}, current time: {}, expired: {}", 
                   expiration, now, expired);
        return expired;
    }

    private Date extractExpiration(String token) {
        return extractClaim(token, Claims::getExpiration);
    }

    private SecretKey getSigningKey() {
        byte[] keyBytes = Decoders.BASE64URL.decode(jwtSecret);
        return Keys.hmacShaKeyFor(keyBytes);
    }

    @Scheduled(fixedRateString = "${jwt.expired-tokens-cleanup-ms}")
    public void cleanupExpiredTokens() {
        tokenRepository.deleteByExpirationDateBefore(Instant.now());
    }

    public void revokeToken(String accessToken) {
        tokenRepository.findByAccessToken(accessToken)
                .ifPresent(token -> {
                    token.setLoggedOut(true);
                    tokenRepository.save(token);
                });
    }

    public void revokeAllTokens(User user) {
        List<Token> tokens = tokenRepository.findAllByUserAndLoggedOutFalse(user);
        logger.info("Revoking {} active tokens for user: {}", tokens.size(), user.getUsername());
        tokens.forEach(token -> {
            logger.info("Revoking token ID: {}", token.getId());
            token.setLoggedOut(true);
            tokenRepository.save(token);
        });
        logger.info("All tokens revoked for user: {}", user.getUsername());
    }

    public Token saveToken(User user, String accessToken, String refreshToken) {
        logger.info("Saving new token for user: {}", user.getUsername());
        logger.info("Access token to save: {}...", accessToken.substring(0, Math.min(20, accessToken.length())));
        Token token = new Token();
        token.setId(uuidService.getRandomUUID());
        token.setAccessToken(accessToken);
        token.setRefreshToken(refreshToken);
        token.setUser(user);
        token.setLoggedOut(false);
        token.setExpirationDate(extractExpiration(accessToken).toInstant());
        Token savedToken = tokenRepository.save(token);
        logger.info("Token saved with ID: {}, loggedOut: {}, access token starts with: {}...", 
                   savedToken.getId(), savedToken.isLoggedOut(), 
                   savedToken.getAccessToken().substring(0, Math.min(20, savedToken.getAccessToken().length())));
        return savedToken;
    }
}