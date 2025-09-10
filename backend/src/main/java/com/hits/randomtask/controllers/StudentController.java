package com.hits.randomtask.controllers;

import com.hits.randomtask.dtos.EventDTO;
import com.hits.randomtask.entities.User;
import com.hits.randomtask.services.EventService;
import com.hits.randomtask.services.StudentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/student")
@RequiredArgsConstructor
public class StudentController {

    private final StudentService studentService;
    private final EventService eventService;

    @GetMapping("/event")
    public ResponseEntity<List<EventDTO>> getAllEvents() {
        return ResponseEntity.ok(eventService.getAllEvents());
    }

    @GetMapping("/event/{id}")
    public ResponseEntity<EventDTO> getEvent(@PathVariable String id) {
        return ResponseEntity.ok(eventService.getEventById(id));
    }

    @PostMapping("/event/{id}/register")
    public ResponseEntity<Void> registerToEvent(
            @PathVariable String id,
            @AuthenticationPrincipal User user
    ) {
        studentService.registerToEvent(id, user);
        return ResponseEntity.ok().build();
    }

    @DeleteMapping("/event/{id}/unregister")
    public ResponseEntity<Void> unregisterFromEvent(
            @PathVariable String id,
            @AuthenticationPrincipal User user
    ) {
        studentService.unregisterFromEvent(id, user);
        return ResponseEntity.ok().build();
    }
}
