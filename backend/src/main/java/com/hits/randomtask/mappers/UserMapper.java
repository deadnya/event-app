package com.hits.randomtask.mappers;

import com.hits.randomtask.dtos.UserDTO;
import com.hits.randomtask.entities.Role;
import com.hits.randomtask.entities.User;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

import java.util.Set;

@Mapper(componentModel = "spring")
public interface UserMapper {
    
    @Mapping(target = "role", expression = "java(getPrimaryRole(user.getRoles()))")
    UserDTO toDTO(User user);
    
    default String getPrimaryRole(Set<Role> roles) {
        return roles.stream()
                .findFirst()
                .map(role -> role.getRole().name())
                .orElse("UNKNOWN");
    }
}
