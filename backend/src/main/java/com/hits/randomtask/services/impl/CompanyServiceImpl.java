package com.hits.randomtask.services.impl;

import com.hits.randomtask.dtos.CompanyShortDTO;
import com.hits.randomtask.mappers.CompanyMapper;
import com.hits.randomtask.repositories.CompanyRepository;
import com.hits.randomtask.services.CompanyService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CompanyServiceImpl implements CompanyService {

    private final CompanyRepository companyRepository;
    private final CompanyMapper companyMapper;

    @Override
    public List<CompanyShortDTO> getAllCompanies() {
        return companyRepository.findAll().stream()
                .map(companyMapper::toShortDTO)
                .toList();
    }
}
