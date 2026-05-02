import React, { useState } from 'react';
import { Brain, Lightbulb, Factory, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, MathText } from './ui';
import { FlipCard } from './FlipCard';

/**
 * Compact Tier 2 revision strip (Pro): mnemonics, flashcards, real-world context.
 * Same data as Tier2View right column; keeps users from hunting inside tier tabs.
 */
export const RevisionPanel = ({ tier2 }) => {
    const [open, setOpen] = useState(true);
    if (!tier2) return null;

    const mnemonics = tier2.mnemonics_memory_aids || [];
    const flashcards = tier2.flashcards || [];
    const contexts = tier2.real_world_context || [];
    if (mnemonics.length === 0 && flashcards.length === 0 && contexts.length === 0) return null;

    return (
        <Card className="p-0 overflow-hidden border border-slate-200 dark:border-border-dark mb-6">
            <button
                type="button"
                onClick={() => setOpen((o) => !o)}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50 dark:bg-white/5 hover:bg-slate-100 dark:hover:bg-white/10 transition-colors"
            >
                <span className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <Lightbulb size={18} className="text-amber-500" />
                    Quick revision
                </span>
                {open ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>
            {open && (
                <div className="p-4 space-y-6 border-t border-slate-200 dark:border-border-dark">
                    {mnemonics.length > 0 && (
                        <div>
                            <h4 className="text-xs font-bold uppercase tracking-wide text-amber-800 dark:text-amber-300 mb-2 flex items-center gap-1">
                                <Brain size={14} /> Mnemonics
                            </h4>
                            <div className="space-y-2">
                                {mnemonics.map((m, i) => (
                                    <div
                                        key={i}
                                        className="bg-amber-50/80 dark:bg-amber-950/30 rounded-lg p-3 border border-amber-100 dark:border-amber-900/40 text-sm"
                                    >
                                        <p className="font-mono font-bold text-amber-900 dark:text-amber-200">
                                            {m.mnemonic?.split(':')[0]}
                                        </p>
                                        <p className="text-slate-700 dark:text-slate-300 italic mt-1">
                                            <MathText>{m.mnemonic?.split(':')[1] || m.mnemonic}</MathText>
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                    {flashcards.length > 0 && (
                        <div>
                            <h4 className="text-xs font-bold uppercase tracking-wide text-purple-700 dark:text-purple-300 mb-2">
                                Flashcards
                            </h4>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                {flashcards.map((fc, i) => (
                                    <FlipCard key={i} card={fc} />
                                ))}
                            </div>
                        </div>
                    )}
                    {contexts.length > 0 && (
                        <div>
                            <h4 className="text-xs font-bold uppercase tracking-wide text-slate-600 dark:text-slate-400 mb-2 flex items-center gap-1">
                                <Factory size={14} /> Real world
                            </h4>
                            <div className="space-y-3 text-sm">
                                {contexts.map((ctx, i) => (
                                    <div key={i} className="rounded-lg border border-slate-200 dark:border-white/10 p-3">
                                        <h5 className="font-bold text-slate-900 dark:text-white">{ctx.application}</h5>
                                        <p className="text-slate-600 dark:text-slate-400 mt-1">{ctx.industry_example}</p>
                                        {ctx.why_it_matters && (
                                            <p className="text-xs text-blue-700 dark:text-blue-300 mt-2 bg-blue-50 dark:bg-blue-950/40 p-2 rounded">
                                                <span className="font-bold">Why it matters:</span> {ctx.why_it_matters}
                                            </p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </Card>
    );
};

export default RevisionPanel;
