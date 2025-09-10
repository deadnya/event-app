package com.hits.randomtask.shared.security;

import com.hits.randomtask.entities.Token;
import com.hits.randomtask.repositories.TokenRepository;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.logout.LogoutHandler;

@Configuration
@RequiredArgsConstructor
public class CustomLogoutHandler implements LogoutHandler {

    private static final Logger logger = LoggerFactory.getLogger(CustomLogoutHandler.class);

    private final TokenRepository tokenRepository;

    @Override
    public void logout(HttpServletRequest request, HttpServletResponse response, Authentication authentication) {
        String authHeader = request.getHeader("Authorization");

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return;
        }

        try {
            String token = authHeader.substring(7);
            Token storedToken = tokenRepository.findByAccessToken(token).orElse(null);

            if (storedToken != null) {
                storedToken.setLoggedOut(true);
                tokenRepository.save(storedToken);
            }
        } catch (Exception ex) {
            logger.error("Logout failed for token", ex);
        }
    }
}