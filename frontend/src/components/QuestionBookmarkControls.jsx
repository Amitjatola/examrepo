import React, { useEffect, useState } from 'react';
import { Bookmark } from 'lucide-react';
import { api } from '../utils/api';
import { useAuth } from '../context/AuthContext';

/**
 * Bookmark toggle + note for current question (logged-in users).
 */
export const QuestionBookmarkControls = ({ questionPublicId }) => {
    const { user } = useAuth();
    const [note, setNote] = useState('');
    const [saved, setSaved] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        setNote('');
        setSaved(false);
        if (!user || !questionPublicId) return undefined;

        let cancelled = false;
        (async () => {
            try {
                const b = await api.get(`/users/me/bookmarks/${encodeURIComponent(questionPublicId)}`);
                if (cancelled) return;
                setSaved(Boolean(b.is_bookmarked));
                setNote(b.note || '');
            } catch {
                if (!cancelled) {
                    setSaved(false);
                    setNote('');
                }
            }
        })();

        return () => {
            cancelled = true;
        };
    }, [user, questionPublicId]);

    const handleToggleBookmark = async () => {
        if (!user || !questionPublicId) {
            window.dispatchEvent(new CustomEvent('open-auth-modal'));
            return;
        }
        setLoading(true);
        try {
            const next = !saved;
            await api.put(`/users/me/bookmarks/${encodeURIComponent(questionPublicId)}`, {
                note,
                is_bookmarked: next,
            });
            setSaved(next);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleSaveNote = async () => {
        if (!user || !questionPublicId || !saved) return;
        setLoading(true);
        try {
            await api.put(`/users/me/bookmarks/${encodeURIComponent(questionPublicId)}`, {
                note,
                is_bookmarked: true,
            });
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (!user) return null;

    return (
        <div className="flex flex-col sm:flex-row sm:items-start gap-3 w-full min-w-0">
            <button
                type="button"
                onClick={handleToggleBookmark}
                disabled={loading}
                aria-pressed={saved}
                aria-label={saved ? 'Remove bookmark' : 'Bookmark question'}
                className={`shrink-0 self-start bg-white dark:bg-card-dark border border-[#e5e7eb] dark:border-border-dark hover:bg-gray-50 dark:hover:bg-white/5 px-3 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2 cursor-pointer ${
                    saved ? 'text-primary border-primary/40' : 'text-slate-900 dark:text-white'
                }`}
            >
                <Bookmark size={18} className={saved ? 'fill-current' : ''} />
                <span className="hidden sm:inline">{saved ? 'Saved' : 'Save'}</span>
            </button>
            <label className="flex flex-1 min-w-0 flex-col gap-1 text-[10px] font-semibold uppercase text-slate-500 dark:text-slate-400">
                Note
                <textarea
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    rows={2}
                    placeholder="Short note…"
                    className="w-full rounded-lg border border-slate-200 dark:border-border-dark bg-white dark:bg-[#1a1d2e] text-xs text-slate-900 dark:text-white px-2 py-1.5 resize-y min-h-[52px]"
                />
                <button
                    type="button"
                    onClick={handleSaveNote}
                    disabled={loading || !saved}
                    className="mt-1 self-end text-[11px] font-bold text-primary hover:underline disabled:opacity-40 cursor-pointer disabled:cursor-not-allowed"
                >
                    Save note
                </button>
            </label>
        </div>
    );
};

export default QuestionBookmarkControls;
