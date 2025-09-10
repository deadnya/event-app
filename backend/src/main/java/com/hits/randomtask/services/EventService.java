package com.hits.randomtask.services;

import com.hits.randomtask.dtos.CreateEventDTO;
import com.hits.randomtask.dtos.EditEventDTO;
import com.hits.randomtask.dtos.EventDTO;
import com.hits.randomtask.entities.User;

import java.util.List;

public interface EventService {
    EventDTO createEvent(CreateEventDTO createEventDTO, User user);
    EventDTO getEventById(String eventId, User user);
    EventDTO getEventById(String eventId);
    List<EventDTO> getAllEvents();
    List<EventDTO> getEventsByCompany(User user);
    void deleteEvent(String eventId, User user);
    EventDTO editEvent(EditEventDTO editEventDTO, User user);
}
