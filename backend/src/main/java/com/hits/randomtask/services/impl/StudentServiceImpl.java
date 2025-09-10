package com.hits.randomtask.services.impl;

import com.hits.randomtask.entities.Event;
import com.hits.randomtask.entities.EventRegistration;
import com.hits.randomtask.entities.User;
import com.hits.randomtask.repositories.EventRegistrationRepository;
import com.hits.randomtask.repositories.EventRepository;
import com.hits.randomtask.repositories.UserRepository;
import com.hits.randomtask.services.StudentService;
import com.hits.randomtask.shared.exceptions.custom.BadRequestException;
import com.hits.randomtask.shared.exceptions.custom.NotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class StudentServiceImpl implements StudentService {

    private final EventRegistrationRepository eventRegistrationRepository;
    private final EventRepository eventRepository;
    private final UserRepository userRepository;

    @Override
    public void registerToEvent(String eventId, User user) {
        if (eventRegistrationRepository.existsByEventIdAndStudentId(eventId, user.getId())) {
            throw new BadRequestException("Student is already registered for this event");
        }

        Event event = eventRepository.findById(eventId).orElseThrow(
                () -> new NotFoundException(String.format("Event with id %s not found", eventId))
        );

        if (event.getDate().isBefore(java.time.LocalDateTime.now())) {
            throw new BadRequestException("Cannot register for an event that has already occurred");
        }

        EventRegistration eventRegistration = new EventRegistration();
        eventRegistration.setEvent(event);
        eventRegistration.setUser(user);

        eventRegistrationRepository.save(eventRegistration);
    }

    @Override
    public void unregisterFromEvent(String eventId, User user) {
        if (!eventRegistrationRepository.existsByEventIdAndStudentId(eventId, user.getId())) {
            throw new BadRequestException("Student is not registered for this event");
        }

        Event event = eventRepository.findById(eventId).orElseThrow(
                () -> new NotFoundException(String.format("Event with id %s not found", eventId))
        );

        if (event.getDate().isBefore(java.time.LocalDateTime.now())) {
            throw new BadRequestException("Cannot unregister from an event that has already occurred");
        }

        eventRegistrationRepository.deleteByEventIdAndStudentId(eventId, user.getId());
    }
}
