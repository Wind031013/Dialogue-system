import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

interface LoginRequest {
    username: string;
    password: string;
}

interface LoginResponse {
    success: boolean;
    message?: string;
    user?: {
        id: number;
        username: string;
        email: string;
        avatar?: string;
    }
}

export const authService = {
    async login(credentials: LoginRequest): Promise<LoginResponse> {
        try {
            const response = await axios.post(`${API_URL}/api/auth/login`, credentials, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            return response.data;
        } catch (error: any) {
            if (error.response) {
                return {
                    success: false,
                    message: error.response.data.message || '登录失败'
                };
            } else {
                return {
                    success: false,
                    message: '网络错误，请稍后重试'
                };
            }
        }
    },

    async register(userData: any): Promise<any> {
        try {
            const response = await axios.post(`${API_URL}/auth/register`, userData);
            return response.data;
        } catch (error: any) {
            throw error;
        }
    }
}