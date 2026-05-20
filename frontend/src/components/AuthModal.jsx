import { useState } from 'react'
import { X, Loader2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { AnimatePresence, motion } from 'framer-motion'
import { GoogleLogin } from '@react-oauth/google'

const AuthModal = () => {
    const {
        authModalOpen,
        closeAuthModal,
        authMode,
        authPromptMessage,
        setAuthMode,
        loginWithGoogle,
        loginWithEmailPassword,
        registerWithEmailPassword,
    } = useAuth()

    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [fullName, setFullName] = useState('')

    const isRegister = authMode === 'register'

    const handleSwitchToLogin = () => {
        setError('')
        setAuthMode('login')
    }

    const handleSwitchToRegister = () => {
        setError('')
        setAuthMode('register')
    }

    const handleGoogleSuccess = async (credentialResponse) => {
        setLoading(true)
        setError('')
        const result = await loginWithGoogle(credentialResponse.credential)
        if (!result.success) setError(result.error)
        setLoading(false)
    }

    const handleGoogleError = () => {
        setError('Google login failed. Please try again.')
    }

    const handleClose = () => {
        setError('')
        setEmail('')
        setPassword('')
        setFullName('')
        closeAuthModal()
    }

    const handleEmailSubmit = async (e) => {
        e.preventDefault()
        if (!email?.trim()) {
            setError('Enter your email')
            return
        }
        if (!password || password.length < 8) {
            setError('Password must be at least 8 characters')
            return
        }

        setLoading(true)
        setError('')

        const result = isRegister
            ? await registerWithEmailPassword(email.trim(), password, fullName.trim())
            : await loginWithEmailPassword(email.trim(), password)

        if (!result.success) setError(result.error)
        setLoading(false)
    }

    return (
        <AnimatePresence>
            {authModalOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
                    onClick={handleClose}
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="auth-modal-title"
                >
                    <motion.div
                        initial={{ opacity: 0, scale: 0.96, y: 8 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.96, y: 8 }}
                        transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
                        onClick={(e) => e.stopPropagation()}
                        className="bg-white dark:bg-[#0c1020] rounded-2xl shadow-[0_24px_80px_rgba(0,0,0,0.35)] w-full max-w-sm overflow-hidden relative border border-slate-200/80 dark:border-white/[0.08]"
                    >
                        <button
                            onClick={handleClose}
                            className="absolute top-4 right-4 p-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-white/10 text-slate-500 dark:text-slate-400 transition-colors z-10"
                            aria-label="Close"
                            tabIndex={0}
                        >
                            <X size={18} />
                        </button>

                        <div className="p-8 pt-9">
                            <AnimatePresence mode="wait">
                                <motion.div
                                    key={authMode}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    transition={{ duration: 0.22, ease: 'easeInOut' }}
                                    className="text-center mb-6"
                                >
                                    <h2
                                        id="auth-modal-title"
                                        className="text-2xl font-bold text-slate-900 dark:text-white mb-2 tracking-tight"
                                    >
                                        {isRegister ? 'Get Started' : 'Welcome Back'}
                                    </h2>
                                    {authPromptMessage ? (
                                        <p className="text-landing-primary dark:text-cyan-400 text-sm font-medium bg-landing-primary/5 dark:bg-cyan-500/10 rounded-lg px-3 py-2 mt-2">
                                            {authPromptMessage}
                                        </p>
                                    ) : (
                                        <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">
                                            {isRegister
                                                ? 'Create your account or continue with Google'
                                                : 'Sign in to your account'}
                                        </p>
                                    )}
                                </motion.div>
                            </AnimatePresence>

                            {error && (
                                <div
                                    id="auth-error"
                                    role="alert"
                                    className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm rounded-lg border border-red-200 dark:border-red-800/30"
                                >
                                    {error}
                                </div>
                            )}

                            <AnimatePresence mode="wait">
                                <motion.div
                                    key={`form-${authMode}`}
                                    initial={{ opacity: 0, y: 6 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -6 }}
                                    transition={{ duration: 0.2 }}
                                >
                                    <form
                                        onSubmit={handleEmailSubmit}
                                        className="mb-4 space-y-3"
                                        aria-label={isRegister ? 'Create account' : 'Sign in'}
                                    >
                                        {isRegister && (
                                            <div>
                                                <label
                                                    htmlFor="auth-name"
                                                    className="block text-left text-xs font-medium text-slate-600 dark:text-slate-300 mb-1"
                                                >
                                                    Full Name
                                                </label>
                                                <input
                                                    id="auth-name"
                                                    type="text"
                                                    autoComplete="name"
                                                    value={fullName}
                                                    onChange={(e) => setFullName(e.target.value)}
                                                    placeholder="Optional"
                                                    className="w-full rounded-lg border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900/50 px-3 py-2.5 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-landing-primary/40 transition-all"
                                                />
                                            </div>
                                        )}
                                        <div>
                                            <label
                                                htmlFor="auth-email"
                                                className="block text-left text-xs font-medium text-slate-600 dark:text-slate-300 mb-1"
                                            >
                                                Email
                                            </label>
                                            <input
                                                id="auth-email"
                                                type="email"
                                                autoComplete="email"
                                                value={email}
                                                onChange={(e) => setEmail(e.target.value)}
                                                className="w-full rounded-lg border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900/50 px-3 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-landing-primary/40 transition-all"
                                                aria-invalid={Boolean(error)}
                                                aria-describedby={error ? 'auth-error' : undefined}
                                            />
                                        </div>
                                        <div>
                                            <label
                                                htmlFor="auth-password"
                                                className="block text-left text-xs font-medium text-slate-600 dark:text-slate-300 mb-1"
                                            >
                                                Password
                                            </label>
                                            <input
                                                id="auth-password"
                                                type="password"
                                                autoComplete={isRegister ? 'new-password' : 'current-password'}
                                                value={password}
                                                onChange={(e) => setPassword(e.target.value)}
                                                className="w-full rounded-lg border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900/50 px-3 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-landing-primary/40 transition-all"
                                                aria-invalid={Boolean(error)}
                                            />
                                        </div>
                                        <button
                                            type="submit"
                                            disabled={loading}
                                            className="w-full rounded-lg bg-landing-primary text-white py-2.5 text-sm font-semibold hover:bg-landing-primary/90 disabled:opacity-50 transition-all mt-1"
                                        >
                                            {loading ? (
                                                <Loader2 size={18} className="animate-spin mx-auto" />
                                            ) : isRegister ? (
                                                'Create Account'
                                            ) : (
                                                'Sign In'
                                            )}
                                        </button>
                                    </form>

                                    <div className="relative flex items-center justify-center my-4">
                                        <div className="absolute inset-0 flex items-center">
                                            <div className="w-full border-t border-slate-200 dark:border-white/[0.06]" />
                                        </div>
                                        <span className="relative bg-white dark:bg-[#0c1020] px-3 text-xs text-slate-400 dark:text-slate-500">
                                            or
                                        </span>
                                    </div>

                                    <div className="flex flex-col items-center justify-center w-full">
                                        <div className="w-full flex justify-center">
                                            <GoogleLogin
                                                onSuccess={handleGoogleSuccess}
                                                onError={handleGoogleError}
                                                useOneTap={false}
                                                text={isRegister ? 'signup_with' : 'signin_with'}
                                                width="100%"
                                            />
                                        </div>
                                    </div>

                                    <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
                                        {isRegister ? (
                                            <>
                                                Already have an account?{' '}
                                                <button
                                                    type="button"
                                                    onClick={handleSwitchToLogin}
                                                    className="font-semibold text-landing-primary dark:text-cyan-400 hover:underline transition-colors"
                                                    tabIndex={0}
                                                >
                                                    Sign in
                                                </button>
                                            </>
                                        ) : (
                                            <>
                                                Don&apos;t have an account?{' '}
                                                <button
                                                    type="button"
                                                    onClick={handleSwitchToRegister}
                                                    className="font-semibold text-landing-primary dark:text-cyan-400 hover:underline transition-colors"
                                                    tabIndex={0}
                                                >
                                                    Get started
                                                </button>
                                            </>
                                        )}
                                    </p>
                                </motion.div>
                            </AnimatePresence>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    )
}

export default AuthModal
