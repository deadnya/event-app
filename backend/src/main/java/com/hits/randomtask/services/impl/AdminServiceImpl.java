package com.hits.randomtask.services.impl;

import com.hits.randomtask.dtos.*;
import com.hits.randomtask.entities.Company;
import com.hits.randomtask.entities.User;
import com.hits.randomtask.mappers.CompanyMapper;
import com.hits.randomtask.mappers.UserMapper;
import com.hits.randomtask.repositories.CompanyRepository;
import com.hits.randomtask.repositories.UserRepository;
import com.hits.randomtask.services.AdminService;
import com.hits.randomtask.services.TelegramNotificationService;
import com.hits.randomtask.services.UUIDService;
import com.hits.randomtask.shared.exceptions.custom.NotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AdminServiceImpl implements AdminService {

    private final CompanyRepository companyRepository;
    private final UserRepository userRepository;
    private final CompanyMapper companyMapper;
    private final UUIDService uuidService;
    private final UserMapper userMapper;
    private final TelegramNotificationService telegramNotificationService;

    @Override
    public void editUserApprovementStatus(String userId, Boolean isApproved, DeclineReasonDTO declineReasonDTO) {

        User user = userRepository.findById(userId).orElseThrow(
                () -> new NotFoundException(String.format("User with id: %s not found", userId))
        );

        if (isApproved) {
            user.setIsApproved(isApproved);
            userRepository.save(user);

            telegramNotificationService.sendApprovalNotification(user);
        } else {
            String reason = declineReasonDTO != null ? declineReasonDTO.reason() : null;

            telegramNotificationService.sendDeclineNotification(user, reason);

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

    @Override
    public List<UserDTO> getPendingUsers() {
        List<User> pendingUsers = userRepository.findAllByIsApprovedFalse();
        return pendingUsers.stream().map(userMapper::toDTO).toList();
    }

    @Override
    public List<UserDTO> getPendingUsersOfMyCompany(User user) {

        if (user.getCompany() == null) {
            throw new NotFoundException("User does not belong to any company");
        }

        List<User> pendingUsers = userRepository.findAllByIsApprovedFalseAndCompany_Id(user.getCompany().getId());
        return pendingUsers.stream().map(userMapper::toDTO).toList();
    }
}
