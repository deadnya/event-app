package com.hits.randomtask.controllers;

import com.hits.randomtask.dtos.CompanyShortDTO;
import com.hits.randomtask.services.CompanyService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/company")
@RequiredArgsConstructor
public class CompanyController {

    private final CompanyService companyService;

    @GetMapping("/all")
    public ResponseEntity<List<CompanyShortDTO>> getAllCompanies() {
        return ResponseEntity.ok(companyService.getAllCompanies());
    }
}