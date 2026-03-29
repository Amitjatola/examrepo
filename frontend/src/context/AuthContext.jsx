import React, { createContext, useState, useEffect, useContext } from 'react';
import { api } from '../utils/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [subscription, setSubscription] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [authModalOpen, setAuthModalOpen] = useState(false);
    const [authMode, setAuthMode] = useState('login'); // 'login' or 'register'
    const [authPromptMessage, setAuthPromptMessage] = useState('');

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
                        // Fetch subscription status
                        await fetchSubscription();
                    }
                    // TODO: In production, validate token with /me endpoint
                } catch (error) {
                    console.error("Token verification failed", error);
                    logout();
                }
            } else {
                setUser(null);
                setSubscription(null);
                localStorage.removeItem('token');
                localStorage.removeItem('user');
            }
            setIsLoading(false);
        };

        verifyToken();
    }, [token]);

    const fetchSubscription = async () => {
        try {
            const data = await api.get('/subscriptions/me');
            setSubscription(data);
        } catch (error) {
            console.error("Failed to fetch subscription:", error);
            setSubscription(null);
        }
    };


    const loginWithGoogle = async (credential) => {
        try {
            const data = await api.post('/auth/google', { token: credential });
            
            // Decode google token for user data
            const base64Url = credential.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            const googleProfile = JSON.parse(jsonPayload);
            
            const userData = { email: googleProfile.email, full_name: googleProfile.name || googleProfile.email.split('@')[0] };
            
            setToken(data.access_token);
            setUser(userData);
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(userData));
            setAuthModalOpen(false);
            
            await fetchSubscription();
            return { success: true };
        } catch (error) {
            console.error("Google Login Error:", error);
            return { success: false, error: 'Google authentication failed' };
        }
    };



    const logout = () => {
        setToken(null);
        setUser(null);
        setSubscription(null);
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
        setAuthPromptMessage('');
    };

    // Helper: checks if user is logged in. If not, opens auth modal with contextual message.
    const requireAuth = (message = '') => {
        if (user) return true;
        setAuthPromptMessage(message);
        setAuthMode('register');
        setAuthModalOpen(true);
        return false;
    };

    return (
        <AuthContext.Provider value={{
            user,
            token,
            subscription,
            isPremium: subscription?.is_premium || false,
            isLoading,
            loginWithGoogle,
            logout,
            fetchSubscription,
            authModalOpen,
            authMode,
            authPromptMessage,
            openLogin,
            openRegister,
            closeAuthModal,
            setAuthMode,
            requireAuth
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
