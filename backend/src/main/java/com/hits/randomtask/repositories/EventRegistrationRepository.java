package com.hits.randomtask.repositories;

import com.hits.randomtask.entities.EventRegistration;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface EventRegistrationRepository extends JpaRepository<EventRegistration, Long> {
    boolean existsByEventIdAndStudentId(String eventId, String studentId);
    void deleteByEventIdAndStudentId(String eventId, String studentId);
}
