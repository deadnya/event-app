package com.hits.randomtask.services.impl;

import com.hits.randomtask.dtos.CreateEventDTO;
import com.hits.randomtask.dtos.EditEventDTO;
import com.hits.randomtask.dtos.EventDTO;
import com.hits.randomtask.entities.Company;
import com.hits.randomtask.entities.Event;
import com.hits.randomtask.entities.User;
import com.hits.randomtask.mappers.EventMapper;
import com.hits.randomtask.repositories.EventRepository;
import com.hits.randomtask.services.EventService;
import com.hits.randomtask.services.UUIDService;
import com.hits.randomtask.shared.exceptions.custom.ForbiddenException;
import com.hits.randomtask.shared.exceptions.custom.NotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class EventServiceImpl implements EventService {

    private final EventRepository eventRepository;
    private final UUIDService uuidService;
    private final EventMapper eventMapper;

    @Override
    public List<EventDTO> getAllEvents() {
        List<Event> events = eventRepository.findAll();
        return events.stream().map(eventMapper::toDTO).toList();
    }

    @Override
    public EventDTO createEvent(CreateEventDTO createEventDTO, User user) {

        Company company = user.getCompany();
        if (company == null) throw new NotFoundException("User is not associated with any company");

        Event event = eventMapper.toEvent(createEventDTO);
        event.setId(uuidService.getRandomUUID());
        event.setCompany(company);

        event = eventRepository.save(event);

        return eventMapper.toDTO(event);
    }

    @Override
    public EventDTO getEventById(String eventId, User user) {

        Event event = eventRepository.findById(eventId).orElseThrow(
                () -> new NotFoundException(String.format("Event with id %s not found", eventId))
        );

        if ((!user.getCompany().getId().equals(event.getCompany().getId()))) {
            throw new ForbiddenException("This event does not belong to your company");
        }

        return eventMapper.toDTO(event);
    }

    @Override
    public EventDTO getEventById(String eventId) {

        Event event = eventRepository.findById(eventId).orElseThrow(
                () -> new NotFoundException(String.format("Event with id %s not found", eventId))
        );

        return eventMapper.toDTO(event);
    }

    @Override
    public void deleteEvent(String eventId, User user) {

        Event event = eventRepository.findById(eventId).orElseThrow(
                () -> new NotFoundException(String.format("Event with id %s not found", eventId))
        );

        if (!user.getCompany().getId().equals(event.getCompany().getId())) {
            throw new ForbiddenException("This event does not belong to your company");
        }

        eventRepository.deleteById(eventId);
    }

    @Override
    public EventDTO editEvent(EditEventDTO editEventDTO, User user) {
        Event event = eventRepository.findById(editEventDTO.id()).orElseThrow(
                () -> new NotFoundException(String.format("Event with id %s not found", editEventDTO.id()))
        );

        if (!user.getCompany().getId().equals(event.getCompany().getId())) {
            throw new ForbiddenException("This event does not belong to your company");
        }

        event.setName(editEventDTO.name());
        event.setDescription(editEventDTO.description());
        event.setDate(editEventDTO.date());
        event.setLocation(editEventDTO.location());

        event = eventRepository.save(event);

        return eventMapper.toDTO(event);
    }
}
