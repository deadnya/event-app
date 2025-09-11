package com.hits.randomtask.services.impl;

import com.hits.randomtask.dtos.EventDTO;
import com.hits.randomtask.entities.Event;
import com.hits.randomtask.entities.EventRegistration;
import com.hits.randomtask.entities.User;
import com.hits.randomtask.mappers.EventMapper;
import com.hits.randomtask.repositories.EventRegistrationRepository;
import com.hits.randomtask.repositories.EventRepository;
import com.hits.randomtask.repositories.UserRepository;
import com.hits.randomtask.services.GoogleCalendarService;
import com.hits.randomtask.services.StudentService;
import com.hits.randomtask.shared.exceptions.custom.BadRequestException;
import com.hits.randomtask.shared.exceptions.custom.NotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class StudentServiceImpl implements StudentService {

    private final EventRegistrationRepository eventRegistrationRepository;
    private final EventRepository eventRepository;
    private final UserRepository userRepository;
    private final EventMapper eventMapper;
    private final GoogleCalendarService googleCalendarService;

    @Override
    public void registerToEvent(String eventId, User user) {
        if (eventRegistrationRepository.existsByEventIdAndUserId(eventId, user.getId())) {
            throw new BadRequestException("Student is already registered for this event");
        }

        Event event = eventRepository.findById(eventId).orElseThrow(
                () -> new NotFoundException(String.format("Event with id %s not found", eventId))
        );

        if (event.getDate().isBefore(java.time.LocalDateTime.now())) {
            throw new BadRequestException("Cannot register for an event that has already occurred");
        }

        if (event.getRegistrationDeadline().isBefore(java.time.LocalDateTime.now())) {
            throw new BadRequestException("Registration deadline has passed");
        }

        EventRegistration eventRegistration = new EventRegistration();
        eventRegistration.setEvent(event);
        eventRegistration.setUser(user);

        // Create Google Calendar event if user has connected their calendar
        if (googleCalendarService.isGoogleCalendarConnected(user)) {
            String googleEventId = googleCalendarService.createCalendarEvent(event, user);
            eventRegistration.setGoogleEventId(googleEventId);
        }

        eventRegistrationRepository.save(eventRegistration);
    }

    @Override
    public void unregisterFromEvent(String eventId, User user) {
        if (!eventRegistrationRepository.existsByEventIdAndUserId(eventId, user.getId())) {
            throw new BadRequestException("Student is not registered for this event");
        }

        Event event = eventRepository.findById(eventId).orElseThrow(
                () -> new NotFoundException(String.format("Event with id %s not found", eventId))
        );

        if (event.getDate().isBefore(java.time.LocalDateTime.now())) {
            throw new BadRequestException("Cannot unregister from an event that has already occurred");
        }

        if (event.getRegistrationDeadline().isBefore(java.time.LocalDateTime.now())) {
            throw new BadRequestException("Registration deadline has passed, cannot unregister");
        }

        // Find the registration to get Google Event ID
        List<EventRegistration> registrations = eventRegistrationRepository.findByUserId(user.getId());
        EventRegistration registration = registrations.stream()
                .filter(reg -> reg.getEvent().getId().equals(eventId))
                .findFirst()
                .orElse(null);

        // Delete Google Calendar event if it exists
        if (registration != null && registration.getGoogleEventId() != null && 
            googleCalendarService.isGoogleCalendarConnected(user)) {
            googleCalendarService.deleteCalendarEvent(registration.getGoogleEventId(), user);
        }

        eventRegistrationRepository.deleteByEventIdAndUserId(eventId, user.getId());
    }

    @Override
    public List<EventDTO> getMyEvents(User user) {
        List<EventRegistration> registrations = eventRegistrationRepository.findByUserId(user.getId());
        return registrations.stream()
                .map(EventRegistration::getEvent)
                .map(eventMapper::toDTO)
                .toList();
    }
}
