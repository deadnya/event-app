package com.hits.randomtask.validators;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.*;

@Documented
@Constraint(validatedBy = EventDatesValidator.class)
@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface ValidEventDates {
    String message() default "Registration deadline must be before event date";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
