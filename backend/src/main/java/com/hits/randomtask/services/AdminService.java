package com.hits.randomtask.services;

import com.hits.randomtask.dtos.CompanyShortDTO;
import com.hits.randomtask.dtos.CreateCompanyDTO;
import com.hits.randomtask.dtos.EditCompanyDTO;

public interface AdminService {
    void editUserApprovementStatus(String userId, Boolean isApproved);
    CompanyShortDTO createCompany(CreateCompanyDTO createCompanyDTO);
    CompanyShortDTO editCompany(EditCompanyDTO editCompanyDTO);
}
