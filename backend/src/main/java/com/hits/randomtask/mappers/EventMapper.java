package com.hits.randomtask.mappers;

import com.hits.randomtask.dtos.CreateEventDTO;
import com.hits.randomtask.dtos.EventDTO;
import com.hits.randomtask.dtos.EventRegistrationDTO;
import com.hits.randomtask.entities.Event;
import com.hits.randomtask.entities.EventRegistration;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface EventMapper {
    EventDTO toDTO(Event event);
    Event toEvent(CreateEventDTO createEventDTO);

    EventRegistrationDTO toDTO(EventRegistration eventRegistration);
}
