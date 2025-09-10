package com.hits.randomtask.repositories;

import com.hits.randomtask.entities.Token;
import com.hits.randomtask.entities.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

@Repository
public interface TokenRepository extends JpaRepository<Token, Integer> {
    Optional<Token> findByAccessToken(String accessToken);
    Optional<Token> findByRefreshToken(String refreshToken);
    List<Token> findAllByUserAndLoggedOutFalse(User user);
    void deleteByExpirationDateBefore(Instant date);
}