package com.hits.randomtask.repositories;

import com.hits.randomtask.entities.EventRegistration;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Repository
public interface EventRegistrationRepository extends JpaRepository<EventRegistration, Long> {
    boolean existsByEventIdAndUserId(String eventId, String userId);
    
    @Modifying
    @Transactional
    void deleteByEventIdAndUserId(String eventId, String userId);
    
    List<EventRegistration> findByUserId(String userId);
}
