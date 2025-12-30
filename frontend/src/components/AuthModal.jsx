import React, { useState } from 'react';
import { X, Mail, Lock, User, Loader2, Eye, EyeOff, ArrowLeft } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { AnimatePresence, motion } from 'framer-motion';

const AuthModal = () => {
    const {
        authModalOpen,
        closeAuthModal,
        authMode,
        setAuthMode,
        login,
        register
    } = useAuth();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [forgotPasswordMode, setForgotPasswordMode] = useState(false);
    const [resetEmailSent, setResetEmailSent] = useState(false);

    if (!authModalOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        let result;
        if (authMode === 'login') {
            result = await login(email, password);
        } else {
            result = await register(email, password, fullName);
        }

        if (!result.success) {
            setError(result.error);
        } else {
            // Clear form on success (modal closes automatically due to success in context)
            setEmail('');
            setPassword('');
            setFullName('');
        }
        setLoading(false);
    };

    const handleForgotPassword = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        // Simulate password reset email sending
        // In production, this would call an API endpoint
        await new Promise(resolve => setTimeout(resolve, 1000));

        setResetEmailSent(true);
        setLoading(false);
    };

    const resetForm = () => {
        setEmail('');
        setPassword('');
        setFullName('');
        setError('');
        setShowPassword(false);
        setForgotPasswordMode(false);
        setResetEmailSent(false);
    };

    const handleClose = () => {
        resetForm();
        closeAuthModal();
    };

    // Forgot Password View
    if (forgotPasswordMode) {
        return (
            <AnimatePresence>
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="bg-white dark:bg-card-dark rounded-2xl shadow-xl w-full max-w-md overflow-hidden relative border border-[#f0f2f4] dark:border-border-dark"
                    >
                        {/* Close Button */}
                        <button
                            onClick={handleClose}
                            className="absolute top-4 right-4 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-white/10 text-slate-500 dark:text-gray-400 transition-colors"
                        >
                            <X size={20} />
                        </button>

                        <div className="p-8">
                            {/* Back Button */}
                            <button
                                onClick={() => { setForgotPasswordMode(false); setResetEmailSent(false); setError(''); }}
                                className="flex items-center gap-2 text-slate-500 dark:text-gray-400 hover:text-primary mb-6 text-sm font-medium transition-colors"
                            >
                                <ArrowLeft size={16} />
                                Back to login
                            </button>

                            <div className="text-center mb-8">
                                <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2 font-display">
                                    Reset Password
                                </h2>
                                <p className="text-slate-500 dark:text-gray-400 text-sm">
                                    {resetEmailSent
                                        ? 'Check your email for reset instructions'
                                        : 'Enter your email to receive reset instructions'
                                    }
                                </p>
                            </div>

                            {error && (
                                <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm rounded-lg border border-red-200 dark:border-red-800/30">
                                    {error}
                                </div>
                            )}

                            {resetEmailSent ? (
                                <div className="text-center space-y-4">
                                    <div className="w-16 h-16 mx-auto bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center">
                                        <Mail size={32} className="text-green-600 dark:text-green-400" />
                                    </div>
                                    <p className="text-slate-600 dark:text-gray-300 text-sm">
                                        We've sent a password reset link to <strong>{email}</strong>
                                    </p>
                                    <button
                                        onClick={() => { setForgotPasswordMode(false); setResetEmailSent(false); }}
                                        className="w-full py-2.5 px-4 bg-primary hover:bg-primary/90 text-white font-medium rounded-xl transition-colors"
                                    >
                                        Back to Login
                                    </button>
                                </div>
                            ) : (
                                <form onSubmit={handleForgotPassword} className="space-y-4">
                                    <div className="space-y-1">
                                        <label className="text-sm font-medium text-slate-700 dark:text-gray-300">Email Address</label>
                                        <div className="relative">
                                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                                <Mail size={18} className="text-gray-400" />
                                            </div>
                                            <input
                                                type="email"
                                                required
                                                value={email}
                                                onChange={(e) => setEmail(e.target.value)}
                                                className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 dark:border-border-dark rounded-xl bg-white dark:bg-background-dark text-slate-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all shadow-sm"
                                                placeholder="you@example.com"
                                            />
                                        </div>
                                    </div>

                                    <button
                                        type="submit"
                                        disabled={loading}
                                        className="w-full py-2.5 px-4 bg-primary hover:bg-primary/90 text-white font-medium rounded-xl transition-colors flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed shadow-[0_0_15px_-3px_rgba(56,88,250,0.4)]"
                                    >
                                        {loading ? <Loader2 size={20} className="animate-spin" /> : 'Send Reset Link'}
                                    </button>
                                </form>
                            )}
                        </div>
                    </motion.div>
                </div>
            </AnimatePresence>
        );
    }

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="bg-white dark:bg-card-dark rounded-2xl shadow-xl w-full max-w-md overflow-hidden relative border border-[#f0f2f4] dark:border-border-dark"
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
                            <p className="text-slate-500 dark:text-gray-400 text-sm">
                                {authMode === 'login' ? 'Enter your details to sign in' : 'Sign up to start tracking your progress'}
                            </p>
                        </div>

                        {error && (
                            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm rounded-lg border border-red-200 dark:border-red-800/30">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-4">
                            {authMode === 'register' && (
                                <div className="space-y-1">
                                    <label className="text-sm font-medium text-slate-700 dark:text-gray-300">Full Name</label>
                                    <div className="relative">
                                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                            <User size={18} className="text-gray-400" />
                                        </div>
                                        <input
                                            type="text"
                                            required
                                            value={fullName}
                                            onChange={(e) => setFullName(e.target.value)}
                                            className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 dark:border-border-dark rounded-xl bg-white dark:bg-background-dark text-slate-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all shadow-sm"
                                            placeholder="John Doe"
                                        />
                                    </div>
                                </div>
                            )}

                            <div className="space-y-1">
                                <label className="text-sm font-medium text-slate-700 dark:text-gray-300">Email Address</label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Mail size={18} className="text-gray-400" />
                                    </div>
                                    <input
                                        type="email"
                                        required
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 dark:border-border-dark rounded-xl bg-white dark:bg-background-dark text-slate-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all shadow-sm"
                                        placeholder="you@example.com"
                                    />
                                </div>
                            </div>

                            <div className="space-y-1">
                                <div className="flex items-center justify-between">
                                    <label className="text-sm font-medium text-slate-700 dark:text-gray-300">Password</label>
                                    {authMode === 'login' && (
                                        <button
                                            type="button"
                                            onClick={() => setForgotPasswordMode(true)}
                                            className="text-xs text-primary hover:underline font-medium"
                                        >
                                            Forgot password?
                                        </button>
                                    )}
                                </div>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Lock size={18} className="text-gray-400" />
                                    </div>
                                    <input
                                        type={showPassword ? 'text' : 'password'}
                                        required
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="block w-full pl-10 pr-10 py-2.5 border border-gray-300 dark:border-border-dark rounded-xl bg-white dark:bg-background-dark text-slate-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all shadow-sm"
                                        placeholder="••••••••"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                                    >
                                        {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                    </button>
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-2.5 px-4 bg-primary hover:bg-primary/90 text-white font-medium rounded-xl transition-colors flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed shadow-[0_0_15px_-3px_rgba(56,88,250,0.4)]"
                            >
                                {loading ? <Loader2 size={20} className="animate-spin" /> : (authMode === 'login' ? 'Sign In' : 'Create Account')}
                            </button>
                        </form>

                        <div className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
                            {authMode === 'login' ? (
                                <>
                                    Don't have an account?{' '}
                                    <button onClick={() => setAuthMode('register')} className="text-primary hover:underline font-medium">
                                        Sign up
                                    </button>
                                </>
                            ) : (
                                <>
                                    Already have an account?{' '}
                                    <button onClick={() => setAuthMode('login')} className="text-primary hover:underline font-medium">
                                        Sign in
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default AuthModal;
