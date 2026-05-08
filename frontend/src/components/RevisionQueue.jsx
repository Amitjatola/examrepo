import React, { useCallback, useEffect, useState } from 'react'
import { ArrowLeft, Loader2, PlayCircle, RefreshCw } from 'lucide-react'
import { api } from '../utils/api'
import { useAuth } from '../context/AuthContext'

const RevisionQueue = ({ onBack, onStartSession }) => {
    const { user, token, isLoading: authLoading, logout } = useAuth()
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [data, setData] = useState({ total_due: 0, items: [] })

    const load = useCallback(async () => {
        const fromStorage = typeof localStorage !== 'undefined' ? localStorage.getItem('token') : null
        if (!token && !fromStorage) {
            setError('Sign in to view your revision queue.')
            setData({ total_due: 0, items: [] })
            setLoading(false)
            return
        }
        if (user && !fromStorage) {
            logout()
            setError('Your session token was missing. Please sign in again.')
            setData({ total_due: 0, items: [] })
            setLoading(false)
            return
        }

        setLoading(true)
        setError(null)
        try {
            const res = await api.getRevisionQueue({ limit: 100, offset: 0 })
            setData(res)
        } catch (e) {
            const msg = e?.message || 'Could not load revision queue'
            const status = e?.status
            if (
                status === 401 ||
                status === 403 ||
                msg === 'Not authenticated' ||
                msg === 'Could not validate credentials'
            ) {
                logout()
                setError('Session expired or not signed in. Please sign in again.')
            } else {
                setError(msg)
            }
            setData({ total_due: 0, items: [] })
        } finally {
            setLoading(false)
        }
    }, [token, user, logout])

    useEffect(() => {
        if (authLoading) return
        if (!user) {
            setLoading(false)
            setError('Sign in to view your revision queue.')
            setData({ total_due: 0, items: [] })
            return
        }
        load()
    }, [authLoading, user, load])

    const handleStartSession = () => {
        const ids = (data.items || []).map((it) => it.revision?.question_id_str).filter(Boolean)
        if (!ids.length) return
        onStartSession?.(ids)
    }

    return (
        <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark min-h-full">
            <div className="max-w-[900px] mx-auto p-6 md:p-8 space-y-6">
                <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                        <button
                            type="button"
                            onClick={() => onBack?.()}
                            className="inline-flex items-center gap-2 text-slate-600 dark:text-gray-400 hover:text-primary cursor-pointer"
                            aria-label="Back"
                        >
                            <ArrowLeft size={20} />
                            <span className="text-sm font-semibold">Back</span>
                        </button>
                    </div>
                    <button
                        type="button"
                        onClick={load}
                        className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 dark:text-gray-400 hover:text-primary cursor-pointer"
                    >
                        <RefreshCw size={16} />
                        Refresh
                    </button>
                </div>

                <div>
                    <h1 className="text-2xl md:text-3xl font-black text-slate-900 dark:text-white font-display">
                        Today’s revision queue
                    </h1>
                    <p className="text-slate-500 dark:text-gray-400 text-sm mt-1">
                        Due cards are ordered by how overdue they are, then hardest first.
                    </p>
                </div>

                {error && (
                    <div className="rounded-lg border border-red-200 dark:border-red-900/40 bg-red-50 dark:bg-red-950/30 px-4 py-3 text-sm text-red-700 dark:text-red-300">
                        {error}
                    </div>
                )}

                <div className="flex flex-wrap items-center justify-between gap-3">
                    <p className="text-slate-700 dark:text-gray-200 text-sm font-semibold">
                        {loading ? 'Loading…' : `${data.total_due} due`}
                    </p>
                    <button
                        type="button"
                        onClick={handleStartSession}
                        disabled={loading || !data.items?.length}
                        className="inline-flex items-center gap-2 rounded-lg bg-primary hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-bold px-5 py-2.5 shadow-sm cursor-pointer"
                    >
                        <PlayCircle size={18} />
                        Start session
                    </button>
                </div>

                {loading ? (
                    <div className="flex justify-center py-16 text-slate-500">
                        <Loader2 className="animate-spin w-10 h-10" aria-label="Loading queue" />
                    </div>
                ) : !data.items?.length ? (
                    <div className="rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-card-dark p-10 text-center text-slate-600 dark:text-gray-400">
                        <p className="font-semibold text-slate-900 dark:text-white mb-2">You’re caught up</p>
                        <p className="text-sm">No questions due for revision right now.</p>
                    </div>
                ) : (
                    <ul className="space-y-3">
                        {data.items.map((it) => {
                            const rev = it.revision
                            const overdue = rev?.days_overdue > 0
                            return (
                                <li
                                    key={rev?.question_id_str || rev?.id}
                                    className="rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-card-dark p-4 flex flex-col gap-2 shadow-sm"
                                >
                                    <div className="flex flex-wrap items-center gap-2 text-xs">
                                        <span className="rounded-full bg-slate-100 dark:bg-white/10 px-2 py-0.5 font-semibold text-slate-700 dark:text-gray-200">
                                            {it.subject || 'Subject'}
                                        </span>
                                        <span className="rounded-full bg-primary/10 text-primary px-2 py-0.5 font-semibold">
                                            {it.year} · Q{it.question_number}
                                        </span>
                                        {it.topic_tag ? (
                                            <span className="rounded-full bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 px-2 py-0.5 font-semibold">
                                                {it.topic_tag}
                                            </span>
                                        ) : null}
                                        <span className="rounded-full bg-slate-50 dark:bg-white/5 px-2 py-0.5 font-semibold text-slate-600 dark:text-gray-400">
                                            ease {rev?.ease_factor?.toFixed?.(2) ?? rev?.ease_factor}
                                        </span>
                                        <span className="rounded-full bg-slate-50 dark:bg-white/5 px-2 py-0.5 font-semibold text-slate-600 dark:text-gray-400">
                                            {rev?.difficulty}
                                        </span>
                                        {overdue ? (
                                            <span className="rounded-full bg-orange-500/15 text-orange-700 dark:text-orange-300 px-2 py-0.5 font-semibold">
                                                {rev.days_overdue}d overdue
                                            </span>
                                        ) : (
                                            <span className="rounded-full bg-green-500/10 text-green-700 dark:text-green-300 px-2 py-0.5 font-semibold">
                                                due now
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-sm text-slate-800 dark:text-gray-100 line-clamp-3">
                                        {it.question_text_preview || '—'}
                                    </p>
                                    <p className="text-[11px] text-slate-400 dark:text-slate-500 font-mono">
                                        {rev?.question_id_str}
                                    </p>
                                </li>
                            )
                        })}
                    </ul>
                )}
            </div>
        </div>
    )
}

export default RevisionQueue
