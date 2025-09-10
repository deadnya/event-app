package com.hits.randomtask.controllers;

import com.hits.randomtask.dtos.UserDTO;
import com.hits.randomtask.entities.User;
import com.hits.randomtask.mappers.UserMapper;
import com.hits.randomtask.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;
    private final UserMapper userMapper;

    @GetMapping("/telegram/{telegramChatId}")
    public ResponseEntity<UserDTO> getUserByTelegramId(@PathVariable Long telegramChatId) {
        User user = userService.findByTelegramChatId(telegramChatId);
        if (user == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(userMapper.toDTO(user));
    }
}