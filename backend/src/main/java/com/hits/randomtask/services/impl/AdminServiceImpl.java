package com.hits.randomtask.services.impl;

import com.hits.randomtask.dtos.CompanyShortDTO;
import com.hits.randomtask.dtos.CreateCompanyDTO;
import com.hits.randomtask.dtos.EditCompanyDTO;
import com.hits.randomtask.entities.Company;
import com.hits.randomtask.entities.User;
import com.hits.randomtask.mappers.CompanyMapper;
import com.hits.randomtask.repositories.CompanyRepository;
import com.hits.randomtask.repositories.UserRepository;
import com.hits.randomtask.services.AdminService;
import com.hits.randomtask.services.UUIDService;
import com.hits.randomtask.shared.exceptions.custom.NotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AdminServiceImpl implements AdminService {

    private final CompanyRepository companyRepository;
    private final UserRepository userRepository;
    private final CompanyMapper companyMapper;
    private final UUIDService uuidService;

    @Override
    public void editUserApprovementStatus(String userId, Boolean isApproved) {

        User user = userRepository.findById(userId).orElseThrow(
                () -> new NotFoundException(String.format("User with id: %s not found", userId))
        );

        if (isApproved) {
            user.setIsApproved(isApproved);
            userRepository.save(user);
        } else {
            userRepository.delete(user);
        }
    }

    @Override
    public CompanyShortDTO createCompany(CreateCompanyDTO createCompanyDTO) {

        Company newCompany = companyMapper.toCompany(createCompanyDTO);
        newCompany.setId(uuidService.getRandomUUID());

        companyRepository.save(newCompany);

        return companyMapper.toShortDTO(newCompany);
    }

    @Override
    public CompanyShortDTO editCompany(EditCompanyDTO editCompanyDTO) {

        Company company = companyRepository.findById(editCompanyDTO.id()).orElseThrow(
                () -> new NotFoundException(String.format("Company with id: %s not found", editCompanyDTO.id()))
        );

        company.setName(editCompanyDTO.name());
        companyRepository.save(company);

        return companyMapper.toShortDTO(company);
    }
}
