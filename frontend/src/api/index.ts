import axios from "axios";
import type { AuthResponseDTO } from "../models/AuthResponseDTO";

export const API_URL = import.meta.env.VITE_API_URL as string;

const $api = axios.create({
    withCredentials: false,
    baseURL: API_URL
});

const $authApi = axios.create({
    withCredentials: false,
    baseURL: API_URL
});

$api.interceptors.request.use((config) => {
    const token = localStorage.getItem('accessToken');
    if (token && token !== 'null' && token !== 'undefined' && token.trim() !== '') {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
})

export { $authApi };

$api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (originalRequest.url === "/auth/refresh") {
            localStorage.clear()
            return Promise.reject(error);
        }
    
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
    
            try {
                console.log("interceptors trying refresh token")
                const refreshToken = localStorage.getItem("refreshToken")
                const response = await $authApi.post<AuthResponseDTO>(
                    "/auth/refresh", 
                    { refreshToken },
                    { withCredentials: false }
                );
                
                localStorage.setItem("refreshToken", response.data.refreshToken ?? "")
                localStorage.setItem("accessToken", response.data.accessToken ?? "")
                originalRequest.headers.Authorization = `Bearer ${response.data.accessToken}`;

                return $api(originalRequest);
            } 
            
            catch (refreshError) {
                console.log("Token Refresh Failed", refreshError)
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default $api