package com.hits.randomtask.controllers;

import com.hits.randomtask.dtos.*;
import com.hits.randomtask.services.AdminService;
import com.hits.randomtask.services.EventService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
@CrossOrigin
public class AdminController {

    private final AdminService adminService;
    private final EventService eventService;

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

    @PostMapping("/company/create")
    public ResponseEntity<CompanyShortDTO> createCompany(@Valid @RequestBody CreateCompanyDTO createCompanyDTO) {
        return ResponseEntity.ok(adminService.createCompany(createCompanyDTO));
    }

    @PutMapping("/company/edit")
    public ResponseEntity<CompanyShortDTO> editCompany(@Valid @RequestBody EditCompanyDTO editCompanyDTO) {
        return ResponseEntity.ok(adminService.editCompany(editCompanyDTO));
    }

    @GetMapping("/event")
    public ResponseEntity<List<EventDTO>> getAllEvents() {
        return ResponseEntity.ok(eventService.getAllEvents());
    }

    @GetMapping("/event/{id}")
    public ResponseEntity<EventDTO> getEvent(@PathVariable String id) {
        return ResponseEntity.ok(eventService.getEventById(id));
    }

    @GetMapping("/users/pending")
    public ResponseEntity<List<UserDTO>> getPendingUsers() {
        return ResponseEntity.ok(adminService.getPendingUsers());
    }
}
