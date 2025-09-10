package com.hits.randomtask.repositories;

import com.hits.randomtask.entities.EventRegistration;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface EventRegistrationRepository extends JpaRepository<EventRegistration, Long> {
    boolean existsByEventIdAndUserId(String eventId, String userId);
    void deleteByEventIdAndUserId(String eventId, String userId);
}
