import React, { createContext, useState, useEffect, useContext } from 'react';
import { api } from '../utils/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [isLoading, setIsLoading] = useState(true);
    const [authModalOpen, setAuthModalOpen] = useState(false);
    const [authMode, setAuthMode] = useState('login'); // 'login' or 'register'

    // Configure API URL from env or default
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

    useEffect(() => {
        const verifyToken = async () => {
            if (token) {
                try {
                    // Try to restore user data from localStorage
                    const storedUser = localStorage.getItem('user');
                    if (storedUser) {
                        setUser(JSON.parse(storedUser));
                    }
                    // TODO: In production, validate token with /me endpoint
                } catch (error) {
                    console.error("Token verification failed", error);
                    logout();
                }
            } else {
                setUser(null);
                localStorage.removeItem('token');
                localStorage.removeItem('user');
            }
            setIsLoading(false);
        };

        verifyToken();
    }, [token]);

    const login = async (email, password) => {
        try {
            const data = await api.post('/auth/login', { email, password });
            const userData = { email, full_name: data.full_name || email.split('@')[0] };
            setToken(data.access_token);
            setUser(userData);
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(userData));
            setAuthModalOpen(false);
            return { success: true };
        } catch (error) {
            console.error("Login Error:", error);
            return { success: false, error: error.message };
        }
    };

    const register = async (email, password, fullName) => {
        try {
            await api.post('/auth/register', { email, password, full_name: fullName });

            // Auto login after register
            return await login(email, password);
        } catch (error) {
            console.error("Register Error:", error);
            return { success: false, error: error.message };
        }
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    };

    const openLogin = () => {
        setAuthMode('login');
        setAuthModalOpen(true);
    };

    const openRegister = () => {
        setAuthMode('register');
        setAuthModalOpen(true);
    };

    const closeAuthModal = () => {
        setAuthModalOpen(false);
    };

    return (
        <AuthContext.Provider value={{
            user,
            token,
            isLoading,
            login,
            register,
            logout,
            authModalOpen,
            authMode,
            openLogin,
            openRegister,
            closeAuthModal,
            setAuthMode
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
