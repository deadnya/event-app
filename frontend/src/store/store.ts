import { makeAutoObservable } from "mobx";
import ApiRequests from "../api/apiRequests";
import type { ProfileDto } from "../models/User";

export default class Store {
    user = {} as ProfileDto
    isAuth = false
    isAdmin = false
    userRole = ""
    isLoading = false
    isRefreshing = false;
    refreshQueue: ((token: string) => void)[] = [];
    isAdminLoading = true

    setAdminLoading(bool: boolean) {
        this.isAdminLoading = bool;
    }

    constructor() {
        makeAutoObservable(this)
    }

    setAuth(bool: boolean) {
        this.isAuth = bool
    }

    setAdmin(bool: boolean) {
        this.isAdmin = bool;
    }

    setUserRole(role: string) {
        this.userRole = role;
        this.setAdmin(role === "ADMIN");
    }

    setUser(user: ProfileDto) {
        this.user = user
    }

    setLoading(bool: boolean) {
        this.isLoading = bool
    }

    clearTokens() {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        this.setAuth(false);
        this.setAdmin(false);
        this.setUserRole("");
    }

    async login(email: string, password: string) {
        this.setLoading(true);
        this.setAdminLoading(true);

        try {
            const response = await ApiRequests.login(email, password);
            console.log(response);

            if (response.status !== 200) {
                throw response;
            }

            if (response.status == 200) {
                if (response.data.accessToken) {
                    localStorage.setItem("accessToken", response.data.accessToken);
                }
                if (response.data.refreshToken) {
                    localStorage.setItem("refreshToken", response.data.refreshToken);
                }
                this.setAuth(true);
                
                const userRole = await ApiRequests.checkUserRole();
                this.setUserRole(userRole);
                
                try {
                    await this.fetchUserProfile();
                } catch (profileError) {
                    console.error("Failed to fetch user profile:", profileError);
                }
                
                return true;
            }

            return false;
        } catch (e) {
            this.setAdmin(false);
            throw e;
        } finally {
            this.setLoading(false);
            this.setAdminLoading(false);
        }
    }

    async loginWithTelegram(data: any) {
        this.setLoading(true);
        this.setAdminLoading(true);

        try {
            this.clearTokens();
            
            const response = await ApiRequests.loginWithTelegram(data);

            if (response.status !== 200) {
                throw response;
            }

            if (response.data.accessToken) {
                localStorage.setItem("accessToken", response.data.accessToken);
            }
            if (response.data.refreshToken) {
                localStorage.setItem("refreshToken", response.data.refreshToken);
            }
            this.setAuth(true);
            
            const userRole = await ApiRequests.checkUserRole();
            this.setUserRole(userRole);
            
            try {
                await this.fetchUserProfile();
            } catch (profileError) {
                console.error("Failed to fetch user profile:", profileError);
            }
            
            return true;
        } catch (e) {
            this.setAdmin(false);
            throw e;
        } finally {
            this.setLoading(false);
            this.setAdminLoading(false);
        }
    }

    async logout () {
        await ApiRequests.logout();
        this.setAuth(false)
        this.setAdmin(false)
        this.setUserRole("")
        this.setLoading(false)
        this.setAdminLoading(false)
    }

    async updateUser(editUserData: { name: { surname: string; name: string; patronymic?: string } }) {
        try {
            await ApiRequests.editUser(editUserData);
            this.setUser({
                ...this.user,
                name: editUserData.name
            });
        } catch (error) {
            console.error("Failed to update user:", error);
            throw error;
        }
    }

    async fetchUserProfile() {
        try {
            const response = await ApiRequests.getUserProfile();
            this.setUser(response.data);
        } catch (error) {
            console.error("Failed to fetch user profile:", error);
            throw error;
        }
    }

    async checkAuth() {
        const refreshToken = localStorage.getItem("refreshToken");
        if (!refreshToken) {
            this.setAdminLoading(false);
            return;
        }

        if (this.isRefreshing) {
            return new Promise<void>((resolve) => {
                this.refreshQueue.push(() => resolve());
            });
        }

        try {
            this.isRefreshing = true;
            const response = await ApiRequests.refresh(refreshToken);
            
            const newAccessToken = response.data.accessToken;
            const newRefreshToken = response.data.refreshToken;
            
            if (newAccessToken) {
                localStorage.setItem("accessToken", newAccessToken);
            }
            if (newRefreshToken) {
                localStorage.setItem("refreshToken", newRefreshToken);
            }
            this.setAuth(true);
            
            const userRole = await ApiRequests.checkUserRole();
            this.setUserRole(userRole);
            
            try {
                await this.fetchUserProfile();
            } catch (profileError) {
                console.error("Failed to fetch user profile:", profileError);
            }
            
            this.refreshQueue.forEach(cb => cb(newAccessToken || ""));
        } catch (e) {
            console.error("Refresh failed", e);
            this.setAuth(false);
            this.setAdmin(false);
            this.setUserRole("");
            localStorage.removeItem("accessToken");
            localStorage.removeItem("refreshToken");
        } finally {
            this.isRefreshing = false;
            this.setAdminLoading(false);
            this.refreshQueue = [];
        }
    }
}