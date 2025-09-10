package com.hits.randomtask.entities;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.Objects;

@Entity
@Getter
@Setter
@NoArgsConstructor
@Table(name = "roles")
public class Role {

    public enum RoleType { ADMIN, MANAGER, STUDENT }

    @Id
    @Column(name = "id", length = 32)
    private String id;

    @Enumerated(EnumType.STRING)
    @Column(unique = true)
    private RoleType role;
}