package com.hits.randomtask.repositories;

import com.hits.randomtask.entities.Event;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface EventRepository extends JpaRepository<Event, String> {
    List<Event> findAllByDateAfterOrderByDateAsc(LocalDateTime date);
    List<Event> findByCompanyId(String companyId);
}
