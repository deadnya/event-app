package com.hits.randomtask.dtos;

import com.hits.randomtask.entities.Role;
import com.hits.randomtask.entities.User;

public record RegisterRequestDTO(
        String email,
        String password,
        String surname,
        String name,
        String patronymic,
        User.Gender gender,
        String group,
        String companyId,
        Role.RoleType role
) { }
