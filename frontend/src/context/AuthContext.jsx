/**
 * Auth + subscription. Freemium rules (hint caps, Pro-only UI) are documented in
 * ../constants/freemium.js — keep product copy aligned with that file.
 */
import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
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

    const fetchSubscription = useCallback(async () => {
        try {
            const data = await api.get('/subscriptions/me');
            setSubscription(data);
        } catch (error) {
            console.error("Failed to fetch subscription:", error);
            setSubscription(null);
        }
    }, []);

    useEffect(() => {
        const verifyToken = async () => {
            if (!token) {
                setUser(null);
                setSubscription(null);
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                setIsLoading(false);
                return;
            }

            setIsLoading(true);
            try {
                // Always validate the JWT with /auth/me on load. Using only cached user + /subscriptions/me
                // caused 401 on subscription to wipe localStorage (before api fix) and skipped expiry checks.
                const me = await api.get('/auth/me')
                const userData = {
                    email: me.email,
                    full_name: me.full_name || me.email.split('@')[0],
                }
                setUser(userData)
                localStorage.setItem('user', JSON.stringify(userData))
                await fetchSubscription()
            } catch (error) {
                console.error("Token verification failed", error)
                setToken(null)
                setUser(null)
                setSubscription(null)
                localStorage.removeItem('token')
                localStorage.removeItem('user')
            } finally {
                setIsLoading(false)
            }
        };

        verifyToken();
    }, [token, fetchSubscription]);

    // Other tabs / external clears: keep React token in sync with localStorage (api.get always reads localStorage).
    useEffect(() => {
        const onStorage = (e) => {
            if (e.key !== 'token') return
            const next = localStorage.getItem('token')
            setToken(next)
            if (!next) {
                setUser(null)
                setSubscription(null)
                localStorage.removeItem('user')
            }
        }
        window.addEventListener('storage', onStorage)
        return () => window.removeEventListener('storage', onStorage)
    }, [])

    useEffect(() => {
        const onFocus = () => {
            const ls = localStorage.getItem('token')
            if (ls !== token) setToken(ls)
        }
        window.addEventListener('focus', onFocus)
        return () => window.removeEventListener('focus', onFocus)
    }, [token])


    const loginWithEmailPassword = async (email, password) => {
        try {
            const data = await api.post('/auth/login', { email, password });
            localStorage.setItem('token', data.access_token);
            setToken(data.access_token);
            const me = await api.get('/auth/me');
            const userData = {
                email: me.email,
                full_name: me.full_name || me.email.split('@')[0],
            };
            setUser(userData);
            localStorage.setItem('user', JSON.stringify(userData));
            setAuthModalOpen(false);
            await fetchSubscription();
            return { success: true };
        } catch (error) {
            console.error('Email login error:', error);
            return {
                success: false,
                error: error?.message || 'Login failed',
            };
        }
    };

    const registerWithEmailPassword = async (email, password, fullName) => {
        try {
            const data = await api.post('/auth/register', { email, password, full_name: fullName || email.split('@')[0] });
            localStorage.setItem('token', data.access_token);
            setToken(data.access_token);
            const me = await api.get('/auth/me');
            const userData = {
                email: me.email,
                full_name: me.full_name || me.email.split('@')[0],
            };
            setUser(userData);
            localStorage.setItem('user', JSON.stringify(userData));
            setAuthModalOpen(false);
            await fetchSubscription();
            return { success: true };
        } catch (error) {
            console.error('Email register error:', error);
            return {
                success: false,
                error: error?.message || 'Registration failed',
            };
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



    const logout = useCallback(() => {
        setToken(null);
        setUser(null);
        setSubscription(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    }, []);

    const openLogin = () => {
        setAuthMode('login');
        setAuthPromptMessage('');
        setAuthModalOpen(true);
    };

    const openRegister = () => {
        setAuthMode('register');
        setAuthPromptMessage('');
        setAuthModalOpen(true);
    };

    const openGetStarted = () => {
        openRegister();
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
            loginWithEmailPassword,
            registerWithEmailPassword,
            logout,
            fetchSubscription,
            authModalOpen,
            authMode,
            authPromptMessage,
            openLogin,
            openRegister,
            openGetStarted,
            closeAuthModal,
            setAuthMode,
            requireAuth
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
