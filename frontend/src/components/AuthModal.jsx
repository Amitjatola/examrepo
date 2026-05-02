import React, { useState } from 'react';
import { X, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { AnimatePresence, motion } from 'framer-motion';
import { GoogleLogin } from '@react-oauth/google';

const emailLoginEnabled = import.meta.env.VITE_ENABLE_EMAIL_LOGIN === 'true';

const AuthModal = () => {
    const {
        authModalOpen,
        closeAuthModal,
        authMode,
        authPromptMessage,
        loginWithGoogle,
        loginWithEmailPassword
    } = useAuth();

    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    if (!authModalOpen) return null;

    const handleGoogleSuccess = async (credentialResponse) => {
        setLoading(true);
        setError('');
        const result = await loginWithGoogle(credentialResponse.credential);
        if (!result.success) {
            setError(result.error);
        }
        setLoading(false);
    };

    const handleGoogleError = () => {
        setError('Google login failed. Please try again.');
    };

    const handleClose = () => {
        setError('');
        setEmail('');
        setPassword('');
        closeAuthModal();
    };

    const handleEmailSubmit = async (e) => {
        e.preventDefault();
        if (!email?.trim() || !password) {
            setError('Enter email and password');
            return;
        }
        setLoading(true);
        setError('');
        const result = await loginWithEmailPassword(email.trim(), password);
        if (!result.success) {
            setError(result.error);
        }
        setLoading(false);
    };

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="bg-white dark:bg-card-dark rounded-2xl shadow-xl w-full max-w-sm overflow-hidden relative border border-[#f0f2f4] dark:border-border-dark"
                >
                    {/* Close Button */}
                    <button
                        onClick={handleClose}
                        className="absolute top-4 right-4 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-white/10 text-slate-500 dark:text-gray-400 transition-colors"
                    >
                        <X size={20} />
                    </button>

                    <div className="p-8">
                        <div className="text-center mb-8">
                            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2 font-display">
                                {authMode === 'login' ? 'Welcome Back' : 'Create Account'}
                            </h2>
                            {/* Contextual prompt message from GatedAction */}
                            {authPromptMessage ? (
                                <p className="text-primary text-sm font-medium bg-primary/5 rounded-lg px-3 py-2 mt-2">
                                    {authPromptMessage}
                                </p>
                            ) : (
                                <p className="text-slate-500 dark:text-gray-400 text-sm">
                                    {emailLoginEnabled
                                        ? 'Sign in with email or continue with Google'
                                        : 'Continue with Google to sign in or sign up'}
                                </p>
                            )}
                        </div>

                        {error && (
                            <div
                                id="auth-error"
                                role="alert"
                                className="mb-6 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm rounded-lg border border-red-200 dark:border-red-800/30"
                            >
                                {error}
                            </div>
                        )}

                        {emailLoginEnabled && (
                            <form
                                onSubmit={handleEmailSubmit}
                                className="mb-6 space-y-3"
                                aria-label="Email sign in"
                            >
                                <div>
                                    <label
                                        htmlFor="auth-email"
                                        className="block text-left text-xs font-medium text-slate-600 dark:text-gray-300 mb-1"
                                    >
                                        Email
                                    </label>
                                    <input
                                        id="auth-email"
                                        type="email"
                                        autoComplete="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="w-full rounded-lg border border-[#e2e8f0] dark:border-border-dark bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40"
                                        aria-invalid={Boolean(error)}
                                        aria-describedby={error ? 'auth-error' : undefined}
                                    />
                                </div>
                                <div>
                                    <label
                                        htmlFor="auth-password"
                                        className="block text-left text-xs font-medium text-slate-600 dark:text-gray-300 mb-1"
                                    >
                                        Password
                                    </label>
                                    <input
                                        id="auth-password"
                                        type="password"
                                        autoComplete="current-password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="w-full rounded-lg border border-[#e2e8f0] dark:border-border-dark bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/40"
                                        aria-invalid={Boolean(error)}
                                    />
                                </div>
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full rounded-lg bg-primary text-white py-2.5 text-sm font-semibold hover:opacity-95 disabled:opacity-50 transition-opacity"
                                >
                                    Sign in with email
                                </button>
                            </form>
                        )}

                        <div className="flex flex-col items-center justify-center w-full relative min-h-[44px]">
                            {loading ? (
                                <div className="absolute inset-0 flex items-center justify-center text-primary bg-white dark:bg-card-dark z-10">
                                    <Loader2 size={24} className="animate-spin" />
                                </div>
                            ) : null}
                            {emailLoginEnabled && (
                                <p className="text-xs text-slate-400 dark:text-gray-500 mb-3 w-full text-center">
                                    or
                                </p>
                            )}
                            <div className="w-full flex justify-center">
                                <GoogleLogin
                                    onSuccess={handleGoogleSuccess}
                                    onError={handleGoogleError}
                                    useOneTap
                                    width="100%"
                                />
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default AuthModal;
