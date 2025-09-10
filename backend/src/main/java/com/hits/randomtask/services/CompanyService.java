package com.hits.randomtask.services;

import com.hits.randomtask.dtos.CompanyShortDTO;

import java.util.List;

public interface CompanyService {
    List<CompanyShortDTO> getAllCompanies();
}
