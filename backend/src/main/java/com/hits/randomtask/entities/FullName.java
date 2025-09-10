package com.hits.randomtask.entities;

import jakarta.persistence.Embeddable;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@Embeddable
public class FullName {
    private String surname;
    private String name;
    private String patronymic;

    public String getFullName() {
        StringBuilder fullName = new StringBuilder();
        fullName.append(surname).append(" ").append(name);
        if (patronymic != null && !patronymic.trim().isEmpty()) {
            fullName.append(" ").append(patronymic);
        }
        return fullName.toString();
    }
}