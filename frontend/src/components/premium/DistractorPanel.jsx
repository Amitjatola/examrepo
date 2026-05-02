import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, MathText } from './ui';

export const DistractorPanel = ({ distractorAnalysis }) => {
    const [open, setOpen] = useState(false);
    const items = distractorAnalysis || [];
    if (!Array.isArray(items) || items.length === 0) return null;

    return (
        <Card className="p-0 overflow-hidden border border-violet-200/80 dark:border-violet-900/40 mb-4">
            <button
                type="button"
                onClick={() => setOpen((o) => !o)}
                className="w-full flex items-center justify-between px-4 py-3 bg-violet-50/80 dark:bg-violet-950/30 hover:bg-violet-50 dark:hover:bg-violet-950/50 transition-colors"
            >
                <span className="text-sm font-bold text-violet-950 dark:text-violet-100 flex items-center gap-2">
                    <HelpCircle size={18} className="text-violet-600" />
                    Why not the other options?
                </span>
                {open ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>
            {open && (
                <ul className="p-4 border-t border-violet-100 dark:border-violet-900/40 space-y-3 text-sm">
                    {items.map((d, i) => (
                        <li
                            key={i}
                            className="rounded-lg border border-violet-100 dark:border-violet-900/30 p-3 bg-white dark:bg-card-dark"
                        >
                            <span className="font-mono font-bold text-violet-700 dark:text-violet-300">
                                {d.option_key || `Option ${i + 1}`}
                            </span>
                            {d.severity && (
                                <span className="ml-2 text-[10px] uppercase font-bold text-slate-400">{d.severity}</span>
                            )}
                            {d.why_wrong && (
                                <p className="mt-2 text-slate-700 dark:text-slate-300">
                                    <MathText>{d.why_wrong}</MathText>
                                </p>
                            )}
                        </li>
                    ))}
                </ul>
            )}
        </Card>
    );
};
