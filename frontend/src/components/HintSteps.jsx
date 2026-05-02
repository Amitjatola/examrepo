import React, { useState, useMemo } from 'react';
import { Lightbulb, ChevronDown, ChevronUp, Lock } from 'lucide-react';
import LatexRenderer from './LatexRenderer';
import { FREE_HINT_STEPS_CAP } from '../constants/freemium';

/**
 * Progressive hints from tier_1 explanation.step_by_step.
 * Free: FREE_HINT_STEPS_CAP steps; Pro: all steps.
 */
const HintSteps = ({
    steps = [],
    isPremium = false,
    questionKey,
    onUpgrade,
    className = '',
}) => {
    const cleanSteps = useMemo(
        () => (Array.isArray(steps) ? steps.filter((s) => s && String(s).trim() !== '') : []),
        [steps]
    );
    const maxFree = FREE_HINT_STEPS_CAP;
    const [revealed, setRevealed] = useState(0);
    const [open, setOpen] = useState(false);

    if (cleanSteps.length === 0) return null;
    const maxReveal = isPremium ? cleanSteps.length : maxFree;

    const canRevealMore = revealed < maxReveal;
    const lockedRemaining = cleanSteps.length - maxReveal;

    const handleNext = () => {
        if (canRevealMore) setRevealed((r) => Math.min(r + 1, maxReveal));
    };

    return (
        <div className={`rounded-xl border border-amber-200/80 dark:border-amber-900/40 bg-amber-50/40 dark:bg-amber-950/20 ${className}`}>
            <button
                type="button"
                onClick={() => setOpen((o) => !o)}
                className="w-full flex items-center justify-between gap-2 px-4 py-3 text-left"
            >
                <span className="flex items-center gap-2 text-sm font-semibold text-amber-900 dark:text-amber-200">
                    <Lightbulb className="shrink-0" size={18} />
                    Stuck? Hints
                    {!isPremium && (
                        <span className="text-xs font-normal text-amber-700/80 dark:text-amber-300/80">
                            ({maxFree} free{lockedRemaining > 0 ? `, ${lockedRemaining} more with Pro` : ''})
                        </span>
                    )}
                </span>
                {open ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>
            {open && (
                <div className="px-4 pb-4 space-y-3 border-t border-amber-200/50 dark:border-amber-900/30 pt-3">
                    {revealed === 0 && (
                        <p className="text-xs text-slate-600 dark:text-slate-400">
                            Reveal one step at a time without opening the full solution.
                        </p>
                    )}
                    <ol className="list-decimal pl-5 space-y-2 text-sm text-slate-800 dark:text-slate-200">
                        {cleanSteps.slice(0, revealed).map((step, idx) => (
                            <li key={`${questionKey}-hint-${idx}`}>
                                <LatexRenderer text={step} />
                            </li>
                        ))}
                    </ol>
                    <div className="flex flex-wrap gap-2 items-center">
                        {canRevealMore && revealed < cleanSteps.length && (
                            <button
                                type="button"
                                onClick={handleNext}
                                className="text-sm font-semibold px-3 py-1.5 rounded-lg bg-amber-600 text-white hover:bg-amber-700 transition-colors"
                            >
                                Next hint
                            </button>
                        )}
                        {!isPremium && revealed >= maxReveal && cleanSteps.length > maxReveal && (
                            <div className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400">
                                <Lock size={14} />
                                <span>Upgrade for all {cleanSteps.length} hints + full solution.</span>
                                {onUpgrade && (
                                    <button
                                        type="button"
                                        onClick={onUpgrade}
                                        className="text-primary font-semibold hover:underline"
                                    >
                                        Go Pro
                                    </button>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default HintSteps;
