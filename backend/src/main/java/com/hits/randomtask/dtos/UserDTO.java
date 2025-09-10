package com.hits.randomtask.dtos;

import com.hits.randomtask.entities.FullName;
import com.hits.randomtask.entities.Role;
import com.hits.randomtask.entities.User;

import java.util.List;

public record UserDTO(
        String id,
        String email,
        Long telegramChatId,
        FullName name,
        User.Gender gender,
        List<Role> roles,
        String role,
        Boolean isApproved,
        String group
) {
}
