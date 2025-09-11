import type { UserDTO } from './User';

export interface EventRegistrationDTO {
    id: number;
    user: UserDTO;
    registeredAt: string;
    googleEventId?: string;
}

export interface EventDTO {
    id: string;
    name: string;
    description?: string;
    location: string;
    date: string;
    registrationDeadline: string;
    registrations: EventRegistrationDTO[];
}

export interface CreateEventDTO {
    name: string;
    description?: string;
    date: string;
    registrationDeadline: string;
    location: string;
}

export interface EditEventDTO {
    id: string;
    name: string;
    description?: string;
    date: string;
    registrationDeadline: string;
    location: string;
}
