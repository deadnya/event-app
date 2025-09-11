package com.hits.randomtask.services;

import com.hits.randomtask.dtos.EventDTO;
import com.hits.randomtask.entities.User;

import java.util.List;

public interface StudentService {
    void registerToEvent(String eventId, User user);
    void unregisterFromEvent(String eventId, User user);
    List<EventDTO> getMyEvents(User user);
}
