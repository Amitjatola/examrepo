import React from 'react';
import { Card, SectionHeader, Badge, MathText } from './ui';
import { AlertTriangle, Brain, Lightbulb, Target, Clock, AlertOctagon, Activity, Factory } from 'lucide-react';
import { FlipCard } from './FlipCard';

export const Tier2View = ({ data }) => {
    if (!data) return null;
    const t2 = data;

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* Column 1: Mistakes & Strategy */}
            <div className="space-y-6">
                <Card className="p-6 border-l-4 border-l-rose-500">
                    <SectionHeader title="Common Mistakes & Traps" icon={<AlertTriangle className="w-5 h-5 text-rose-500" />} />
                    <div className="space-y-6">
                        {t2.common_mistakes.map((mistake, i) => (
                            <div key={i} className="bg-rose-50/50 p-4 rounded-lg border border-rose-100">
                                <div className="flex justify-between items-start mb-2">
                                    <div>
                                        <h4 className="font-semibold text-rose-900 text-sm"><MathText inline>{mistake.mistake}</MathText></h4>
                                        <div className="flex gap-2 mt-1">
                                            <span className="text-[10px] uppercase font-bold text-rose-600 bg-white px-1 rounded border border-rose-200">{mistake.type}</span>
                                            <span className="text-[10px] uppercase font-bold text-rose-600 bg-white px-1 rounded border border-rose-200">Freq: {mistake.frequency}</span>
                                        </div>
                                    </div>
                                    <Badge variant="red">{mistake.severity}</Badge>
                                </div>
                                <p className="text-sm text-rose-800 mb-3"><MathText>{mistake.why_students_make_it}</MathText></p>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                                    <div className="bg-white p-2 rounded border border-rose-100">
                                        <span className="font-bold text-rose-700 block mb-1">How to avoid:</span>
                                        <MathText>{mistake.how_to_avoid}</MathText>
                                    </div>
                                    <div className="bg-white p-2 rounded border border-rose-100">
                                        <span className="font-bold text-rose-700 block mb-1">Consequence:</span>
                                        <MathText>{mistake.consequence}</MathText>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>

                <Card className="p-6">
                    <SectionHeader title="Exam Strategy" icon={<Target className="w-5 h-5 text-blue-500" />} />
                    <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="bg-slate-50 p-3 rounded-lg text-center">
                            <p className="text-xs text-slate-500 uppercase font-bold">Priority</p>
                            <p className="font-bold text-slate-900 dark:text-white">{t2.exam_strategy.priority}</p>
                        </div>
                        <div className="bg-slate-50 p-3 rounded-lg text-center">
                            <p className="text-xs text-slate-500 uppercase font-bold">Time Allocation</p>
                            <p className="font-bold text-slate-900 dark:text-white flex items-center justify-center gap-1">
                                <Clock className="w-3 h-3" /> {t2.exam_strategy.time_management}
                            </p>
                        </div>
                    </div>

                    <div className="space-y-3">
                        <div className="flex gap-3 items-start">
                            <div className="shrink-0 mt-1"><Activity className="w-4 h-4 text-blue-500" /></div>
                            <div>
                                <p className="text-xs font-bold text-slate-500 uppercase">Triage Tip</p>
                                <p className="text-sm text-slate-800"><MathText>{t2.exam_strategy.triage_tip}</MathText></p>
                            </div>
                        </div>
                        <div className="flex gap-3 items-start">
                            <div className="shrink-0 mt-1"><AlertOctagon className="w-4 h-4 text-orange-500" /></div>
                            <div>
                                <p className="text-xs font-bold text-slate-500 uppercase">Guessing Heuristic</p>
                                <p className="text-sm text-slate-800"><MathText>{t2.exam_strategy.guessing_heuristic}</MathText></p>
                            </div>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Column 2: Memory & Context */}
            <div className="space-y-6">
                <Card className="p-6 bg-amber-50 border-amber-200">
                    <SectionHeader title="Mnemonics & Memory Aids" icon={<Brain className="w-5 h-5 text-amber-600" />} />
                    <div className="space-y-4">
                        {t2.mnemonics_memory_aids.map((m, i) => (
                            <div key={i} className="bg-white p-4 rounded-xl shadow-sm border border-amber-100">
                                <div className="flex items-center gap-2 mb-2">
                                    <span className="bg-amber-100 text-amber-800 text-xs font-bold px-2 py-1 rounded uppercase">Mnemonic</span>
                                    <span className="text-xs text-slate-400">Effectiveness: {m.effectiveness}</span>
                                </div>
                                <p className="font-mono font-bold text-lg text-amber-900 mb-1">{m.mnemonic.split(':')[0]}</p>
                                <p className="text-sm text-slate-700 italic"><MathText>{m.mnemonic.split(':')[1] || m.mnemonic}</MathText></p>
                                <div className="mt-3 pt-2 border-t border-amber-50">
                                    <p className="text-xs text-slate-500"><span className="font-bold text-amber-800">Concept:</span> {m.concept}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>

                <Card className="p-6">
                    <SectionHeader title="Flashcards" icon={<Lightbulb className="w-5 h-5 text-purple-500" />} />
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {t2.flashcards.map((fc, i) => (
                            <FlipCard key={i} card={fc} />
                        ))}
                    </div>
                </Card>

                <Card className="p-6">
                    <SectionHeader title="Real World Context" icon={<Factory className="w-5 h-5 text-slate-500" />} />
                    <div className="space-y-4">
                        {t2.real_world_context.map((ctx, i) => (
                            <div key={i} className="text-sm">
                                <h5 className="font-bold text-slate-900 dark:text-white">{ctx.application}</h5>
                                <p className="text-slate-600 mb-2">{ctx.industry_example}</p>
                                <p className="text-xs text-blue-600 bg-blue-50 p-2 rounded">
                                    <span className="font-bold">Why it matters:</span> {ctx.why_it_matters}
                                </p>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
        </div>
    );
};
