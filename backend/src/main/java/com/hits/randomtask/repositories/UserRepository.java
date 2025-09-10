package com.hits.randomtask.repositories;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import com.hits.randomtask.entities.User;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, String> {
    Optional<User> findByEmail(@Param("email") String email);
    Optional<User> findByTelegramChatId(@Param("telegramChatId") Long telegramChatId);
}