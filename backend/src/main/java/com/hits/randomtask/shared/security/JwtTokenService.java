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
        return Jwts
                .builder()
                .subject(user.getUsername())
                .issuedAt(new Date(System.currentTimeMillis()))
                .expiration(new Date(System.currentTimeMillis() + expireTime ))
                .signWith(getSigningKey())
                .compact();
    }

    public String extractUsername(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    public <T> T extractClaim(String token, Function<Claims, T> resolver) {
        Claims claims = extractAllClaims(token);
        return resolver.apply(claims);
    }

    private Claims extractAllClaims(String token) {
        return Jwts
                .parser()
                .verifyWith(getSigningKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    public boolean isValid(String token, UserDetails user) {
        String username = extractUsername(token);

        boolean validToken = tokenRepository
                .findByAccessToken(token)
                .map(t -> !t.isLoggedOut())
                .orElse(false);

        return (username.equals(user.getUsername())) && isTokenExpired(token) && validToken;
    }

    public boolean isValidRefreshToken(String token, User user) {
        String username = extractUsername(token);

        boolean validRefreshToken = tokenRepository
                .findByRefreshToken(token)
                .map(t -> !t.isLoggedOut())
                .orElse(false);

        return (username.equals(user.getUsername())) && isTokenExpired(token) && validRefreshToken;
    }

    private boolean isTokenExpired(String token) {
        return !extractExpiration(token).before(new Date());
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
        tokens.forEach(token -> {
            token.setLoggedOut(true);
            tokenRepository.save(token);
        });
    }

    public Token saveToken(User user, String accessToken, String refreshToken) {
        Token token = new Token();
        token.setId(uuidService.getRandomUUID());
        token.setAccessToken(accessToken);
        token.setRefreshToken(refreshToken);
        token.setUser(user);
        token.setLoggedOut(false);
        token.setExpirationDate(extractExpiration(accessToken).toInstant());
        return tokenRepository.save(token);
    }
}