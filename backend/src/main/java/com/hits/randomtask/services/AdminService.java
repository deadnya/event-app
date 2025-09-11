package com.hits.randomtask.services;

import com.hits.randomtask.dtos.*;
import com.hits.randomtask.entities.User;

import java.util.List;

public interface AdminService {
    void editUserApprovementStatus(String userId, Boolean isApproved, DeclineReasonDTO declineReasonDTO);
    CompanyShortDTO createCompany(CreateCompanyDTO createCompanyDTO);
    CompanyShortDTO editCompany(EditCompanyDTO editCompanyDTO);
    List<UserDTO> getPendingUsers();
    List<UserDTO> getPendingUsersOfMyCompany(User user);
}
