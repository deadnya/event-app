package com.hits.randomtask.services.impl;

import com.hits.randomtask.services.UUIDService;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class UUIDServiceImpl implements UUIDService {
    @Override
    public String getRandomUUID() {
        return UUID.randomUUID().toString().replace("-", "");
    }
}