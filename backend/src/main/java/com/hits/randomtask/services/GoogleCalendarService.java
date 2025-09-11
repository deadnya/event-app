package com.hits.randomtask.services;

import com.hits.randomtask.entities.Event;
import com.hits.randomtask.entities.User;

public interface GoogleCalendarService {
    String getAuthorizationUrl(User user);
    void handleCallback(String code, User user);
    void disconnectGoogleCalendar(User user);
    String createCalendarEvent(Event event, User user);
    void deleteCalendarEvent(String googleEventId, User user);
    boolean isGoogleCalendarConnected(User user);
}
