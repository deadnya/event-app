import type { AxiosResponse } from "axios";
import $api, { $authApi } from "../api";
import type { AuthResponseDTO } from "../models/AuthResponseDTO";
import type { TelegramLoginRequestDTO } from "../models/Auth";
import type { UserDTO, EditUserDTO } from "../models/User";
import type { EventDTO, CreateEventDTO, EditEventDTO } from "../models/Event";
import type { CompanyShortDTO, CreateCompanyDTO, EditCompanyDTO } from "../models/Company";
import type { DeclineReasonDTO } from "../models/DeclineReason";

export default class ApiRequests {
    static async checkAdminPermission(): Promise<boolean> {
        try {
            await $api.get("/admin/event", {
                params: { page: "1", pageSize: "1" }
            });
            return true;
        } catch (error: any) {
            if (error.response?.status === 403) {
                return false;
            }
            return false;
        }
    }

    static async checkUserRole(): Promise<string> {
        try {
            await $api.get("/admin/event");
            return "ADMIN";
        } catch (error: any) {
            try {
                await $api.get("/manager/events");
                return "MANAGER";
            } catch (managerError: any) {
                try {
                    await $api.get("/student/events");
                    return "STUDENT";
                } catch (studentError: any) {
                    return "UNKNOWN";
                }
            }
        }
    }

    static async refresh(refreshToken: string): Promise<AxiosResponse<AuthResponseDTO>> {
        return $authApi.post<AuthResponseDTO>("/auth/refresh", { refreshToken });
    }

    static async logout(): Promise<AxiosResponse<void>> {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        return Promise.resolve({ data: undefined } as AxiosResponse<void>);
    }

    static async login(email: string, password: string): Promise<AxiosResponse<AuthResponseDTO>> {
        return $authApi.post<AuthResponseDTO>("/auth/login", { email, password });
    }

    static async loginWithTelegram(data: TelegramLoginRequestDTO): Promise<AxiosResponse<AuthResponseDTO>> {
        return $authApi.post<AuthResponseDTO>("/auth/telegram-login", data);
    }

    static async getUserByTelegramId(telegramChatId: number): Promise<AxiosResponse<UserDTO>> {
        return $api.get<UserDTO>(`/users/telegram/${telegramChatId}`);
    }

    static async getUserProfile(): Promise<AxiosResponse<UserDTO>> {
        return $api.get<UserDTO>("/users/profile");
    }

    static async editUser(data: EditUserDTO): Promise<AxiosResponse<void>> {
        return $api.put<void>("/users/edit", data);
    }

    static async getStudentEvents(): Promise<AxiosResponse<EventDTO[]>> {
        return $api.get<EventDTO[]>("/student/events");
    }

    static async getAllEvents(): Promise<AxiosResponse<EventDTO[]>> {
        return $api.get<EventDTO[]>("/student/event");
    }

    static async getEventById(id: string): Promise<AxiosResponse<EventDTO>> {
        return $api.get<EventDTO>(`/student/event/${id}`);
    }

    static async registerToEvent(id: string): Promise<AxiosResponse<void>> {
        return $api.post<void>(`/student/event/${id}/register`);
    }

    static async unregisterFromEvent(id: string): Promise<AxiosResponse<void>> {
        return $api.delete<void>(`/student/event/${id}/unregister`);
    }

    static async getManagerEvents(): Promise<AxiosResponse<EventDTO[]>> {
        return $api.get<EventDTO[]>("/manager/events");
    }

    static async createEvent(data: CreateEventDTO): Promise<AxiosResponse<EventDTO>> {
        return $api.post<EventDTO>("/manager/event/create", data);
    }

    static async editEvent(data: EditEventDTO): Promise<AxiosResponse<EventDTO>> {
        return $api.put<EventDTO>("/manager/event/edit", data);
    }

    static async deleteEvent(id: string): Promise<AxiosResponse<void>> {
        return $api.delete<void>(`/manager/event/${id}`);
    }

    static async approveUser(userId: string): Promise<AxiosResponse<void>> {
        return $api.patch<void>(`/admin/approve-user/${userId}`);
    }

    static async declineUser(userId: string, declineReason?: DeclineReasonDTO): Promise<AxiosResponse<void>> {
        return $api.patch<void>(`/admin/decline-user/${userId}`, declineReason || { reason: undefined });
    }

    static async getAllCompanies(): Promise<AxiosResponse<CompanyShortDTO[]>> {
        return $api.get<CompanyShortDTO[]>("/company/all");
    }

    static async createCompany(data: CreateCompanyDTO): Promise<AxiosResponse<CompanyShortDTO>> {
        return $api.post<CompanyShortDTO>("/admin/company/create", data);
    }

    static async editCompany(data: EditCompanyDTO): Promise<AxiosResponse<CompanyShortDTO>> {
        return $api.put<CompanyShortDTO>("/admin/company/edit", data);
    }

    static async getAdminEvents(): Promise<AxiosResponse<EventDTO[]>> {
        return $api.get<EventDTO[]>("/admin/event");
    }

    static async getAdminEventById(id: string): Promise<AxiosResponse<EventDTO>> {
        return $api.get<EventDTO>(`/admin/event/${id}`);
    }

    static async getPendingUsers(): Promise<AxiosResponse<UserDTO[]>> {
        return $api.get<UserDTO[]>("/admin/users/pending");
    }

    static async getGoogleCalendarAuthUrl(): Promise<AxiosResponse<{ authUrl?: string; error?: string }>> {
        return $api.get<{ authUrl?: string; error?: string }>("/google-calendar/auth-url");
    }

    static async handleGoogleCalendarCallback(code: string, state?: string): Promise<AxiosResponse<{ message: string }>> {
        const params: any = { code };
        if (state) {
            params.state = state;
        }
        return $api.post<{ message: string }>("/google-calendar/callback", null, { params });
    }

    static async disconnectGoogleCalendar(): Promise<AxiosResponse<{ message: string }>> {
        return $api.delete<{ message: string }>("/google-calendar/disconnect");
    }

    static async getGoogleCalendarStatus(): Promise<AxiosResponse<{ connected: boolean }>> {
        return $api.get<{ connected: boolean }>("/google-calendar/status");
    }
}

export const googleCalendarApi = {
    getAuthUrl: () => ApiRequests.getGoogleCalendarAuthUrl(),
    handleCallback: (code: string, state?: string) => ApiRequests.handleGoogleCalendarCallback(code, state),
    disconnect: () => ApiRequests.disconnectGoogleCalendar(),
    getStatus: () => ApiRequests.getGoogleCalendarStatus()
};