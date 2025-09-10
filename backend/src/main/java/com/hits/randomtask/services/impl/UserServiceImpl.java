package com.hits.randomtask.services.impl;

import com.hits.randomtask.dtos.TelegramRegistrationDTO;
import com.hits.randomtask.entities.Company;
import com.hits.randomtask.entities.FullName;
import com.hits.randomtask.entities.Role;
import com.hits.randomtask.entities.User;
import com.hits.randomtask.repositories.CompanyRepository;
import com.hits.randomtask.repositories.RoleRepository;
import com.hits.randomtask.repositories.UserRepository;
import com.hits.randomtask.services.UUIDService;
import com.hits.randomtask.services.UserService;
import com.hits.randomtask.shared.exceptions.custom.AuthException;
import com.hits.randomtask.shared.exceptions.custom.BadRequestException;
import com.hits.randomtask.shared.exceptions.custom.NotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Set;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final CompanyRepository companyRepository;
    private final UUIDService uuidService;

    @Override
    public User findByEmail(String email) {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new NotFoundException(String.format("User with email: %s not found", email)));
    }

    @Override
    public User findByID(String id) {
        return userRepository.findById(id)
                .orElseThrow(
                        () -> new NotFoundException(String.format("User with id: %s not found", id))
                );
    }

    @Override
    public User findByTelegramId(Long telegramId) {
        return userRepository.findByTelegramChatId(telegramId)
                .orElseThrow(() -> new NotFoundException(String.format("User with telegramId: %d not found", telegramId)));
    }

    @Override
    @Transactional
    public User registerTelegramUser(TelegramRegistrationDTO registrationDTO) {
        if (userRepository.findByTelegramChatId(registrationDTO.telegramChatId()).isPresent()) {
            throw new AuthException("User with this Telegram ID already exists");
        }

        Role.RoleType roleType;
        try {
            roleType = Role.RoleType.valueOf(registrationDTO.role().toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new AuthException("Invalid role: " + registrationDTO.role());
        }

        Role role = roleRepository.findByRole(roleType)
                .orElseThrow(() -> new AuthException("Role not found: " + roleType));

        User user = new User();
        user.setId(uuidService.getRandomUUID());

        FullName fullName = new FullName();
        fullName.setSurname(registrationDTO.surname());
        fullName.setName(registrationDTO.name());
        fullName.setPatronymic(registrationDTO.patronymic());
        user.setName(fullName);

        user.setEmail(null);
        user.setPassword(null);

        user.setTelegramChatId(registrationDTO.telegramChatId());
        user.setTelegramUsername(registrationDTO.telegramUsername());

        user.setRoles(Set.of(role));

        if (roleType == Role.RoleType.STUDENT) {
            if (registrationDTO.group() == null || registrationDTO.group().trim().isEmpty()) {
                throw new AuthException("Group is required for students");
            }
            user.setGroup(registrationDTO.group());
        } else if (roleType == Role.RoleType.MANAGER) {
            if (registrationDTO.companyId() == null || registrationDTO.companyId().trim().isEmpty()) {
                throw new AuthException("Company ID is required for managers");
            }

            Company company = companyRepository.findById(registrationDTO.companyId())
                    .orElseThrow(() -> new AuthException("Company not found: " + registrationDTO.companyId()));
            user.setCompany(company);
        }

        user.setIsApproved(false);

        return userRepository.save(user);
    }

    @Override
    public User findByTelegramChatId(Long telegramChatId) {
        return userRepository.findByTelegramChatId(telegramChatId)
                .orElse(null);
    }
}