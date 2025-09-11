export interface FullName {
    surname: string;
    name: string;
    patronymic?: string;
}

export const Gender = {
    FEMALE: 'FEMALE',
    MALE: 'MALE'
} as const;

export type Gender = typeof Gender[keyof typeof Gender];

export const RoleType = {
    ADMIN: 'ADMIN',
    MANAGER: 'MANAGER',
    STUDENT: 'STUDENT'
} as const;

export type RoleType = typeof RoleType[keyof typeof RoleType];

export interface Role {
    id: string;
    role: RoleType;
}

export interface UserDTO {
    id: string;
    email?: string;
    telegramChatId?: number;
    name: FullName;
    gender: Gender;
    roles: Role[];
    role: string;
    isApproved: boolean;
    group?: string;
}

export interface EditUserDTO {
    name: FullName;
}

export interface ProfileDto extends UserDTO {}
