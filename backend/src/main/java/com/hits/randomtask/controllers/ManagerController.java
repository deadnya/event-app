package com.hits.randomtask.controllers;

import com.hits.randomtask.dtos.*;
import com.hits.randomtask.entities.User;
import com.hits.randomtask.services.AdminService;
import com.hits.randomtask.services.EventService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/manager")
@RequiredArgsConstructor
@CrossOrigin
public class ManagerController {

    private final EventService eventService;
    private final AdminService adminService; //to refactor later

    @GetMapping("/events")
    public ResponseEntity<List<EventDTO>> getCompanyEvents(@AuthenticationPrincipal User user) {
        return ResponseEntity.ok(eventService.getEventsByCompany(user));
    }

    @PostMapping("/event/create")
    public ResponseEntity<EventDTO> createEvent(
            @Valid @RequestBody CreateEventDTO createEventDTO,
            @AuthenticationPrincipal User user
    ) {
        return ResponseEntity.ok(eventService.createEvent(createEventDTO, user));
    }

    @GetMapping("/event/{id}")
    public ResponseEntity<EventDTO> getEvent(
            @PathVariable String id,
            @AuthenticationPrincipal User user
    ) {
        return ResponseEntity.ok(eventService.getEventById(id, user));
    }

    @PutMapping("/event/edit")
    public ResponseEntity<EventDTO> editEvent(
            @Valid @RequestBody EditEventDTO editEventDTO,
            @AuthenticationPrincipal User user
    ) {
        return ResponseEntity.ok(eventService.editEvent(editEventDTO, user));
    }

    @DeleteMapping("/event/{id}")
    public ResponseEntity<Void> deleteEvent(
            @PathVariable String id,
            @AuthenticationPrincipal User user
    ) {
        eventService.deleteEvent(id, user);
        return ResponseEntity.ok().build();
    }

    @PatchMapping("/approve-user/{userId}")
    public ResponseEntity<Void> approveUser(@PathVariable String userId) {
        adminService.editUserApprovementStatus(userId, true, null);
        return ResponseEntity.ok().build();
    }

    @PatchMapping("/decline-user/{userId}")
    public ResponseEntity<Void> declineUser(@PathVariable String userId, @Valid @RequestBody DeclineReasonDTO declineReasonDTO) {
        adminService.editUserApprovementStatus(userId, false, declineReasonDTO);
        return ResponseEntity.ok().build();
    }

    @GetMapping("/users/pending")
    public ResponseEntity<List<UserDTO>> getPendingUsersOfMyCompany(
            @AuthenticationPrincipal User user
    ) {
        return ResponseEntity.ok(adminService.getPendingUsersOfMyCompany(user));
    }
}
