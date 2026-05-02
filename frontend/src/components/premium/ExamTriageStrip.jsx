import React, { useState } from 'react';
import { Clock, Gauge, Target, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, MathText } from './ui';
import { EXAM_TRIAGE_FREE_PREVIEW } from '../../constants/freemium';

/**
 * Exam-day triage from Tier 2 strategy + Tier 1 difficulty signals.
 */
export const ExamTriageStrip = ({ tier1, tier2, isPremium, onUpgrade }) => {
    const [open, setOpen] = useState(true);
    const strategy = tier2?.exam_strategy;
    const da = tier1?.difficulty_analysis;

    if (!strategy && !da) return null;

    const priority = strategy?.priority;
    const timeMgmt = strategy?.time_management;
    const triageTip = strategy?.triage_tip;
    const guess = strategy?.guessing_heuristic;
    const estSec = da?.estimated_solve_time_seconds;
    const expAcc = da?.expected_accuracy_percent;
    const overall = da?.overall;

    const previewLine =
        triageTip || priority || (overall != null ? `Difficulty: ${overall}` : null);
    if (!previewLine && estSec == null && expAcc == null) return null;

    return (
        <Card className="p-0 overflow-hidden border border-amber-200/80 dark:border-amber-900/40 mb-4">
            <button
                type="button"
                onClick={() => setOpen((o) => !o)}
                className="w-full flex items-center justify-between px-4 py-3 bg-amber-50/90 dark:bg-amber-950/30 hover:bg-amber-50 dark:hover:bg-amber-950/50 transition-colors"
            >
                <span className="text-sm font-bold text-amber-950 dark:text-amber-100 flex items-center gap-2">
                    <Target size={18} className="text-amber-600" />
                    Exam triage
                </span>
                {open ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>
            {open && (
                <div className="px-4 py-3 border-t border-amber-100 dark:border-amber-900/40 space-y-3 text-sm">
                    {!isPremium && EXAM_TRIAGE_FREE_PREVIEW && previewLine && (
                        <>
                            <p className="text-slate-800 dark:text-slate-200">
                                <MathText>{previewLine}</MathText>
                            </p>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                <button
                                    type="button"
                                    onClick={onUpgrade}
                                    className="text-primary font-semibold hover:underline"
                                >
                                    Upgrade to Pro
                                </button>{' '}
                                for full time targets, guessing heuristics, and accuracy expectations.
                            </p>
                        </>
                    )}
                    {isPremium && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            {priority && (
                                <div className="rounded-lg border border-slate-200 dark:border-white/10 p-3">
                                    <span className="text-[10px] font-bold uppercase text-slate-400">Priority</span>
                                    <p className="font-semibold text-slate-900 dark:text-white mt-1">{priority}</p>
                                </div>
                            )}
                            {(estSec != null || expAcc != null || overall != null) && (
                                <div className="rounded-lg border border-slate-200 dark:border-white/10 p-3 flex flex-wrap gap-3">
                                    {estSec != null && (
                                        <div className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300">
                                            <Clock size={14} className="text-slate-400" />
                                            <span>~{estSec}s target</span>
                                        </div>
                                    )}
                                    {expAcc != null && (
                                        <div className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300">
                                            <Gauge size={14} className="text-slate-400" />
                                            <span>~{expAcc}% expected accuracy</span>
                                        </div>
                                    )}
                                    {overall != null && (
                                        <div className="w-full text-xs text-slate-500">Overall: {String(overall)}</div>
                                    )}
                                </div>
                            )}
                            {timeMgmt && (
                                <div className="sm:col-span-2 rounded-lg border border-slate-200 dark:border-white/10 p-3">
                                    <span className="text-[10px] font-bold uppercase text-slate-400">Time</span>
                                    <p className="text-slate-800 dark:text-slate-200 mt-1">
                                        <MathText>{timeMgmt}</MathText>
                                    </p>
                                </div>
                            )}
                            {triageTip && (
                                <div className="sm:col-span-2 rounded-lg border border-slate-200 dark:border-white/10 p-3">
                                    <span className="text-[10px] font-bold uppercase text-slate-400">Triage</span>
                                    <p className="text-slate-800 dark:text-slate-200 mt-1">
                                        <MathText>{triageTip}</MathText>
                                    </p>
                                </div>
                            )}
                            {guess && (
                                <div className="sm:col-span-2 rounded-lg border border-emerald-100 dark:border-emerald-900/40 bg-emerald-50/50 dark:bg-emerald-950/20 p-3">
                                    <span className="text-[10px] font-bold uppercase text-emerald-800 dark:text-emerald-300">
                                        Guessing
                                    </span>
                                    <p className="text-slate-800 dark:text-slate-200 mt-1">
                                        <MathText>{guess}</MathText>
                                    </p>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </Card>
    );
};
