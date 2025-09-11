package com.hits.randomtask.validators;

import com.hits.randomtask.dtos.CreateEventDTO;
import com.hits.randomtask.dtos.EditEventDTO;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

public class EventDatesValidator implements ConstraintValidator<ValidEventDates, Object> {

    @Override
    public void initialize(ValidEventDates constraintAnnotation) {
    }

    @Override
    public boolean isValid(Object dto, ConstraintValidatorContext context) {
        if (dto instanceof CreateEventDTO createEventDTO) {
            return createEventDTO.registrationDeadline().isBefore(createEventDTO.date()) ||
                   createEventDTO.registrationDeadline().isEqual(createEventDTO.date());
        }
        if (dto instanceof EditEventDTO editEventDTO) {
            return editEventDTO.registrationDeadline().isBefore(editEventDTO.date()) ||
                   editEventDTO.registrationDeadline().isEqual(editEventDTO.date());
        }
        return true;
    }
}
