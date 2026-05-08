import React, { useEffect, useState, useCallback } from 'react';
import { ArrowLeft, Loader2, Medal, Shield, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';

const SORT_OPTIONS = [
    { id: 'composite', label: 'Composite score' },
    { id: 'accuracy', label: 'Accuracy' },
    { id: 'questions_solved', label: 'Questions solved' },
];

const Leaderboard = ({ onBack }) => {
    const { user, openLogin } = useAuth();
    const [sortBy, setSortBy] = useState('composite');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [info, setInfo] = useState(null);
    const [infoLoading, setInfoLoading] = useState(true);
    const [visibilityBusy, setVisibilityBusy] = useState(false);

    const loadBoard = useCallback(async () => {
        if (!user) return;
        setLoading(true);
        setError(null);
        try {
            const res = await api.getLeaderboard({ sort_by: sortBy, limit: 50, offset: 0 });
            setData(res);
        } catch (e) {
            setError(e.message || 'Could not load leaderboard');
            setData(null);
        } finally {
            setLoading(false);
        }
    }, [user, sortBy]);

    useEffect(() => {
        if (!user) {
            setInfoLoading(false);
            return undefined;
        }
        let cancelled = false;
        (async () => {
            try {
                const i = await api.getLeaderboardInfo();
                if (!cancelled) setInfo(i);
            } catch {
                if (!cancelled) setInfo(null);
            } finally {
                if (!cancelled) setInfoLoading(false);
            }
        })();
        return () => {
            cancelled = true;
        };
    }, [user]);

    useEffect(() => {
        loadBoard();
    }, [loadBoard]);

    const handleVisibilityChange = async (next) => {
        setVisibilityBusy(true);
        try {
            const updated = await api.updateLeaderboardVisibility(next);
            setInfo(updated);
            await loadBoard();
        } catch (e) {
            setError(e.message || 'Could not update visibility');
        } finally {
            setVisibilityBusy(false);
        }
    };

    if (!user) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-8 max-w-lg mx-auto text-center gap-4">
                <p className="text-slate-600 dark:text-slate-300">Sign in to view the leaderboard and your stats.</p>
                <button
                    type="button"
                    onClick={() => openLogin?.()}
                    className="rounded-lg bg-primary px-6 py-3 text-white font-bold hover:bg-blue-600"
                >
                    Log in
                </button>
                {onBack ? (
                    <button type="button" onClick={onBack} className="text-sm text-primary font-semibold">
                        Back
                    </button>
                ) : null}
            </div>
        );
    }

    const topPct =
        data?.current_user_percentile != null && data.total_participants > 0
            ? Math.max(1, Math.ceil(Number(data.current_user_percentile)))
            : null;

    const rankMedal = (rank) => {
        if (rank === 1) return 'text-amber-500';
        if (rank === 2) return 'text-slate-400 dark:text-slate-300';
        if (rank === 3) return 'text-amber-700 dark:text-amber-600';
        return 'text-slate-300 dark:text-slate-600';
    };

    return (
        <div className="flex-1 flex flex-col h-full overflow-hidden bg-background-light dark:bg-background-dark">
            <div className="shrink-0 border-b border-slate-200 dark:border-border-dark px-4 sm:px-6 py-4 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                    <button
                        type="button"
                        onClick={onBack}
                        className="inline-flex items-center gap-2 text-slate-600 dark:text-slate-300 hover:text-primary font-medium text-sm shrink-0"
                        aria-label="Back"
                    >
                        <ArrowLeft size={18} aria-hidden />
                        Back
                    </button>
                    <h1 className="text-xl font-bold text-slate-900 dark:text-white truncate">Leaderboard</h1>
                </div>

                <div className="flex flex-wrap items-center gap-2 text-xs sm:text-sm">
                    <span className="text-slate-500 dark:text-slate-400 font-medium">Show as:</span>
                    <button
                        type="button"
                        disabled={visibilityBusy || infoLoading || (info?.visibility || 'anonymous') === 'anonymous'}
                        onClick={() => handleVisibilityChange('anonymous')}
                        className={`inline-flex items-center gap-1 rounded-lg px-3 py-1.5 font-bold border ${
                            (info?.visibility || 'anonymous') === 'anonymous'
                                ? 'bg-primary/10 border-primary text-primary'
                                : 'border-slate-200 dark:border-border-dark text-slate-600 dark:text-slate-300'
                        }`}
                        aria-pressed={(info?.visibility || 'anonymous') === 'anonymous'}
                    >
                        <EyeOff size={14} aria-hidden />
                        Anonymous
                    </button>
                    <button
                        type="button"
                        disabled={visibilityBusy || infoLoading || info?.visibility === 'public'}
                        onClick={() => handleVisibilityChange('public')}
                        className={`inline-flex items-center gap-1 rounded-lg px-3 py-1.5 font-bold border ${
                            info?.visibility === 'public'
                                ? 'bg-primary/10 border-primary text-primary'
                                : 'border-slate-200 dark:border-border-dark text-slate-600 dark:text-slate-300'
                        }`}
                        aria-pressed={info?.visibility === 'public'}
                    >
                        <Eye size={14} aria-hidden />
                        Public name
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 max-w-4xl mx-auto w-full space-y-6">
                {info?.alias ? (
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                        Your anonymous handle: <span className="font-mono font-semibold text-slate-700 dark:text-slate-200">{info.alias}</span>
                    </p>
                ) : null}

                {topPct != null && data?.current_user_rank != null ? (
                    <div className="rounded-xl border border-primary/30 bg-primary/5 dark:bg-primary/10 px-4 py-3 flex items-center gap-3">
                        <Shield size={22} className="text-primary shrink-0" aria-hidden />
                        <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">
                            You are in the <span className="text-primary">top {topPct}%</span>
                            {data.current_user_rank ? ` (rank #${data.current_user_rank} of ${data.total_participants})` : null}.
                        </p>
                    </div>
                ) : data && data.total_participants === 0 ? (
                    <div className="rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] p-4 text-sm text-slate-600 dark:text-slate-300">
                        Not enough activity yet — solve some questions to appear on the leaderboard!
                    </div>
                ) : data?.current_user_rank == null && !loading ? (
                    <div className="rounded-xl border border-amber-200 dark:border-amber-900/40 bg-amber-50/80 dark:bg-amber-950/20 px-4 py-3 text-sm text-amber-950 dark:text-amber-100">
                        You have no attempts yet. Practice a few questions to join the rankings.
                    </div>
                ) : null}

                <div className="flex flex-wrap gap-2">
                    {SORT_OPTIONS.map((opt) => (
                        <button
                            key={opt.id}
                            type="button"
                            onClick={() => setSortBy(opt.id)}
                            className={`rounded-lg px-3 py-2 text-xs font-bold border transition-colors ${
                                sortBy === opt.id
                                    ? 'bg-primary text-white border-primary'
                                    : 'border-slate-200 dark:border-border-dark text-slate-600 dark:text-slate-300 hover:border-primary/50'
                            }`}
                            aria-pressed={sortBy === opt.id}
                        >
                            {opt.label}
                        </button>
                    ))}
                </div>

                {error ? (
                    <div className="rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 px-4 py-2 text-sm" role="alert">
                        {error}
                    </div>
                ) : null}

                {loading ? (
                    <div className="flex justify-center py-12">
                        <Loader2 className="animate-spin text-primary" size={28} aria-label="Loading" />
                    </div>
                ) : !data?.entries?.length ? (
                    <p className="text-sm text-slate-500 dark:text-slate-400 text-center py-8">
                        No ranked learners yet — be the first to practice.
                    </p>
                ) : (
                    <ul className="space-y-2 pb-8">
                        {data.entries.map((row, idx) => (
                            <li
                                key={`lb-row-${idx}`}
                                className={`rounded-xl border px-4 py-3 flex flex-wrap items-center gap-3 ${
                                    row.is_current_user
                                        ? 'border-primary bg-primary/5 dark:bg-primary/10'
                                        : 'border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b]'
                                }`}
                            >
                                <div className="flex items-center gap-2 w-16 shrink-0">
                                    {row.rank <= 3 ? (
                                        <Medal size={20} className={rankMedal(row.rank)} aria-hidden />
                                    ) : null}
                                    <span className="text-sm font-black text-slate-500 dark:text-slate-400">#{row.rank}</span>
                                </div>
                                <div className="flex-1 min-w-[140px]">
                                    <p className="font-semibold text-slate-900 dark:text-white truncate">{row.display_name}</p>
                                    {row.is_current_user ? (
                                        <p className="text-[10px] font-bold text-primary uppercase tracking-wide">You</p>
                                    ) : null}
                                </div>
                                <div className="flex flex-wrap gap-3 text-xs text-slate-600 dark:text-slate-300">
                                    <span>
                                        <span className="font-bold text-slate-900 dark:text-white">{row.questions_solved}</span> solved
                                    </span>
                                    <span>
                                        <span className="font-bold text-slate-900 dark:text-white">{row.accuracy_pct}%</span> acc
                                    </span>
                                    <span>
                                        <span className="font-bold text-slate-900 dark:text-white">{row.revision_streak}</span> rev streak
                                    </span>
                                    <span>
                                        Score <span className="font-bold text-primary">{row.composite_score}</span>
                                    </span>
                                </div>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};

export default Leaderboard;
