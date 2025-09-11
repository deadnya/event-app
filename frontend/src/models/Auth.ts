export interface LoginRequestDTO {
    email: string;
    password: string;
}

export interface TelegramLoginRequestDTO {
    id: number;
    firstName: string;
    lastName?: string;
    username?: string;
    authDate: number;
    hash: string;
}

export interface RefreshRequestDTO {
    refreshToken: string;
}
