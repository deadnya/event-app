package com.hits.randomtask.mappers;

import com.hits.randomtask.dtos.UserDTO;
import com.hits.randomtask.entities.User;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface UserMapper {
    UserDTO toDTO(User user);
}
