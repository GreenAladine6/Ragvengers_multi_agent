import api from './api';
import { User } from '../types';

interface LoginResponse {
    access_token: string;
    token_type: string;
}

export const login = async (email: string, password: string): Promise<LoginResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', email); // OAuth2PasswordRequestForm expects username
    formData.append('password', password);

    try {
        const response = await api.post<LoginResponse>('/token', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
        }
        return response.data;
    } catch (error: any) {
        console.error("Login API Error:", error.response?.data || error.message);
        throw error;
    }
};

export const register = async (email: string, password: string, role: string): Promise<any> => {
    let endpoint = '/users/clients/';
    let payload: any = { email, password };

    if (role === 'employee' || role === 'admin') {
        endpoint = '/users/employees/';
        payload = { email, password, role };
    }

    const response = await api.post(endpoint, payload);
    return response.data;
};

export const logout = () => {
    localStorage.removeItem('token');
};

export const getCurrentUser = async (): Promise<User> => {
    const response = await api.get<any>('/users/me');
    const data = response.data;
    
    // Map backend response to frontend User interface
    return {
        id: data.id_client || data.id_employee || data.id || '',
        name: data.name || data.email?.split('@')[0] || 'User',
        email: data.email || '',
        role: (data.role || 'client') as any,
        avatar: data.avatar,
    };
};

export const isAuthenticated = (): boolean => {
    return !!localStorage.getItem('token');
};
