import React, { useEffect, useState, useCallback } from 'react';
import { Lightbulb, Lock, Sparkles } from 'lucide-react';
import { api } from '../utils/api';
import { cn } from './premium/ui';

const GapDetectorCard = ({
    questionId,
    isPremium,
    onStartDrill,
    onUpgrade,
    emphasizeAfterWrong = false,
}) => {
    const [loading, setLoading] = useState(false);
    const [payload, setPayload] = useState(null);

    const load = useCallback(async () => {
        if (!questionId || !isPremium) {
            setPayload(null);
            return;
        }
        setLoading(true);
        try {
            const data = await api.getGapDrill(questionId);
            setPayload(data);
        } catch {
            setPayload(null);
        } finally {
            setLoading(false);
        }
    }, [questionId, isPremium]);

    useEffect(() => {
        load();
    }, [load]);

    if (!isPremium) {
        return (
            <div className="rounded-xl border border-slate-200 dark:border-border-dark bg-slate-50/80 dark:bg-[#15192b]/80 p-5">
                <div className="flex items-start gap-3">
                    <div className="shrink-0 p-2 rounded-lg bg-primary/10 text-primary">
                        <Lock size={20} aria-hidden />
                    </div>
                    <div className="min-w-0 flex-1">
                        <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <Lightbulb size={16} className="text-amber-500" aria-hidden />
                            Guided gap drills
                        </h3>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                            Pro unlocks warmup playlists built from official prerequisite tags for this question.
                        </p>
                        <button
                            type="button"
                            onClick={() => onUpgrade?.()}
                            className="mt-3 inline-flex items-center gap-2 rounded-lg bg-primary hover:bg-blue-600 px-4 py-2 text-xs font-bold text-white"
                            aria-label="Upgrade to Pro for gap drills"
                        >
                            <Sparkles size={14} aria-hidden />
                            Upgrade to Pro
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (loading || !payload?.question_ids?.length) {
        return null;
    }

    const handleStart = () => {
        onStartDrill?.({
            questionIds: payload.question_ids,
            labels: payload.prerequisite_labels || [],
            originalQuestionId: payload.original_question_id || questionId,
        });
    };

    return (
        <div
            className={cn(
                'rounded-xl border p-5 transition-shadow',
                emphasizeAfterWrong
                    ? 'border-amber-400 dark:border-amber-600/60 bg-amber-50/90 dark:bg-amber-950/25 shadow-md ring-2 ring-amber-400/50 dark:ring-amber-600/40'
                    : 'border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b]',
            )}
        >
            <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="flex items-start gap-2 min-w-0">
                    <Lightbulb size={20} className="text-amber-500 shrink-0 mt-0.5" aria-hidden />
                    <div className="min-w-0">
                        <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                            {emphasizeAfterWrong
                                ? 'Based on your answer — review these concepts first'
                                : 'Fill knowledge gaps'}
                        </h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            {payload.total_found} warmup question{payload.total_found !== 1 ? 's' : ''} from prerequisite
                            tags
                        </p>
                    </div>
                </div>
            </div>
            <div className="flex flex-wrap gap-1.5 mt-3">
                {(payload.prerequisite_labels || []).map((label) => (
                    <span
                        key={label}
                        className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-slate-100 dark:bg-white/10 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-white/10 max-w-full truncate"
                        title={label}
                    >
                        {label}
                    </span>
                ))}
            </div>
            <div className="mt-4 flex flex-wrap gap-2 justify-end">
                <button
                    type="button"
                    onClick={handleStart}
                    className="inline-flex items-center gap-2 rounded-lg bg-primary hover:bg-blue-600 px-4 py-2 text-xs font-bold text-white"
                    aria-label="Start gap drill playlist"
                >
                    Start gap drill
                </button>
            </div>
        </div>
    );
};

export default GapDetectorCard;
