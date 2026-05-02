import React, { useState } from 'react';
import { ArrowRightLeft, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, MathText } from './ui';

export const AlternativeMethodsSection = ({ alternativeMethods, defaultOpen = false }) => {
    const [open, setOpen] = useState(defaultOpen);
    const methods = alternativeMethods || [];
    if (methods.length === 0) return null;

    return (
        <Card className="p-0 overflow-hidden border border-emerald-200/80 dark:border-emerald-900/40 mb-4">
            <button
                type="button"
                onClick={() => setOpen((o) => !o)}
                className="w-full flex items-center justify-between px-4 py-3 bg-emerald-50/80 dark:bg-emerald-950/30 hover:bg-emerald-50 dark:hover:bg-emerald-950/50 transition-colors"
            >
                <span className="text-sm font-bold text-emerald-950 dark:text-emerald-100 flex items-center gap-2">
                    <ArrowRightLeft size={18} className="text-emerald-600" />
                    Alternative tags
                </span>
                {open ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>
            {open && (
                <div className="p-4 border-t border-emerald-100 dark:border-emerald-900/40 space-y-4">
                    {methods.map((method, i) => (
                        <div key={i} className="bg-white dark:bg-card-dark p-4 rounded-xl border border-slate-200 dark:border-border-dark">
                            <h4 className="font-bold text-slate-900 dark:text-white mb-2">{method.name}</h4>
                            {method.description && (
                                <p className="text-slate-700 dark:text-slate-300 text-sm mb-3">
                                    <MathText>{method.description}</MathText>
                                </p>
                            )}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                                {method.pros_cons && (
                                    <div className="bg-slate-50 dark:bg-white/5 p-3 rounded-lg border border-slate-100 dark:border-white/10">
                                        <span className="text-[10px] font-bold text-slate-400 uppercase">Pros & cons</span>
                                        <div className="mt-1 text-slate-700 dark:text-slate-300">
                                            <MathText>{method.pros_cons}</MathText>
                                        </div>
                                    </div>
                                )}
                                {method.when_to_use && (
                                    <div className="bg-emerald-50/80 dark:bg-emerald-950/30 p-3 rounded-lg border border-emerald-100 dark:border-emerald-900/40">
                                        <span className="text-[10px] font-bold text-emerald-800 dark:text-emerald-300 uppercase">
                                            When to use
                                        </span>
                                        <p className="mt-1 text-emerald-900 dark:text-emerald-100">{method.when_to_use}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </Card>
    );
};
