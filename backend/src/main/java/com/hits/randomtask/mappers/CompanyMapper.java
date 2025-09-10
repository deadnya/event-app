package com.hits.randomtask.mappers;

import com.hits.randomtask.dtos.CompanyShortDTO;
import com.hits.randomtask.entities.Company;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface CompanyMapper {
    CompanyShortDTO toShortDTO(Company company);
}