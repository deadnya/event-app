package com.hits.randomtask.controllers;

import com.hits.randomtask.dtos.EditUserDTO;
import com.hits.randomtask.dtos.UserDTO;
import com.hits.randomtask.entities.User;
import com.hits.randomtask.mappers.UserMapper;
import com.hits.randomtask.services.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/users")
@CrossOrigin
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

    @PutMapping("/edit")
    public ResponseEntity<Void> editUser(
            @RequestBody EditUserDTO editUserDTO,
            @AuthenticationPrincipal User user
    ) {
        userService.editUser(editUserDTO, user);
        return ResponseEntity.ok().build();
    }

    @GetMapping("/profile")
    public ResponseEntity<UserDTO> getUserProfile(@AuthenticationPrincipal User user) {
        return ResponseEntity.ok(userMapper.toDTO(user));
    }
}