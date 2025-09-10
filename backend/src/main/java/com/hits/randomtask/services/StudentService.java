package com.hits.randomtask.services;

import com.hits.randomtask.entities.User;

public interface StudentService {
    void registerToEvent(String eventId, User user);
    void unregisterFromEvent(String eventId, User user);
}
