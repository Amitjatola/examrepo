import React from 'react'
import { Card, SectionHeader, Badge, MathText } from './ui'
import { AlertTriangle, Brain, Lightbulb, Target, Clock, AlertOctagon, Activity, Factory } from 'lucide-react'
import { FlipCard } from './FlipCard'

/** Common mistakes / traps — reuse in Tier2 tab + QuestionDetail Deep Dive */
export const CommonMistakesSection = ({ mistakes }) => {
    const items = mistakes || []
    if (!items.length) return null
    return (
        <Card className="p-6 border-l-4 border-l-rose-500 dark:border-l-rose-600">
            <SectionHeader title="Common Mistakes & Traps" icon={<AlertTriangle className="w-5 h-5 text-rose-500" />} />
            <div className="space-y-6">
                {items.map((mistake, i) => (
                    <div key={i} className="bg-rose-50/50 dark:bg-rose-950/30 p-4 rounded-lg border border-rose-100 dark:border-rose-900/40">
                        <div className="flex justify-between items-start mb-2 gap-2">
                            <div className="min-w-0">
                                <h4 className="font-semibold text-rose-900 dark:text-rose-100 text-sm">
                                    <MathText inline>{mistake.mistake}</MathText>
                                </h4>
                                <div className="flex gap-2 mt-1 flex-wrap">
                                    <span className="text-[10px] uppercase font-bold text-rose-600 dark:text-rose-400 bg-white dark:bg-card-dark px-1 rounded border border-rose-200 dark:border-rose-800">
                                        {mistake.type}
                                    </span>
                                    <span className="text-[10px] uppercase font-bold text-rose-600 dark:text-rose-400 bg-white dark:bg-card-dark px-1 rounded border border-rose-200 dark:border-rose-800">
                                        Freq: {mistake.frequency}
                                    </span>
                                </div>
                            </div>
                            <Badge variant="red">{mistake.severity}</Badge>
                        </div>
                        <p className="text-sm text-rose-800 dark:text-rose-200 mb-3">
                            <MathText>{mistake.why_students_make_it}</MathText>
                        </p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                            <div className="bg-white dark:bg-card-dark p-2 rounded border border-rose-100 dark:border-rose-900/50">
                                <span className="font-bold text-rose-700 dark:text-rose-300 block mb-1">How to avoid:</span>
                                <MathText>{mistake.how_to_avoid || 'N/A'}</MathText>
                            </div>
                            <div className="bg-white dark:bg-card-dark p-2 rounded border border-rose-100 dark:border-rose-900/50">
                                <span className="font-bold text-rose-700 dark:text-rose-300 block mb-1">Consequence:</span>
                                <MathText>{mistake.consequence || 'N/A'}</MathText>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </Card>
    )
}

/** Full exam strategy card (beyond ExamTriageStrip one-liners) */
export const ExamStrategyDetailSection = ({ examStrategy }) => {
    if (!examStrategy) return null
    return (
        <Card className="p-6 border border-slate-200 dark:border-border-dark">
            <SectionHeader title="Exam Strategy" icon={<Target className="w-5 h-5 text-blue-500" />} />
            <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-slate-50 dark:bg-white/5 p-3 rounded-lg text-center">
                    <p className="text-xs text-slate-500 dark:text-slate-400 uppercase font-bold">Priority</p>
                    <p className="font-bold text-slate-900 dark:text-white">{examStrategy.priority || 'Standard'}</p>
                </div>
                <div className="bg-slate-50 dark:bg-white/5 p-3 rounded-lg text-center">
                    <p className="text-xs text-slate-500 dark:text-slate-400 uppercase font-bold">Time allocation</p>
                    <p className="font-bold text-slate-900 dark:text-white flex items-center justify-center gap-1">
                        <Clock className="w-3 h-3" /> {examStrategy.time_management || 'Standard'}
                    </p>
                </div>
            </div>
            <div className="space-y-3">
                <div className="flex gap-3 items-start">
                    <div className="shrink-0 mt-1">
                        <Activity className="w-4 h-4 text-blue-500" />
                    </div>
                    <div>
                        <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase">Triage tip</p>
                        <p className="text-sm text-slate-800 dark:text-slate-200">
                            <MathText>{examStrategy.triage_tip || 'Default triage strategy applies.'}</MathText>
                        </p>
                    </div>
                </div>
                <div className="flex gap-3 items-start">
                    <div className="shrink-0 mt-1">
                        <AlertOctagon className="w-4 h-4 text-orange-500" />
                    </div>
                    <div>
                        <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase">Guessing heuristic</p>
                        <p className="text-sm text-slate-800 dark:text-slate-200">
                            <MathText>{examStrategy.guessing_heuristic || 'No specific guessing heuristic.'}</MathText>
                        </p>
                    </div>
                </div>
            </div>
        </Card>
    )
}

export const MnemonicsSection = ({ mnemonics }) => {
    const items = mnemonics || []
    if (!items.length) return null
    return (
        <Card className="p-6 bg-amber-50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-900/40">
            <SectionHeader title="Mnemonics & Memory Aids" icon={<Brain className="w-5 h-5 text-amber-600" />} />
            <div className="space-y-4">
                {items.map((m, i) => {
                    const raw = typeof m.mnemonic === 'string' ? m.mnemonic : ''
                    const head = raw.includes(':') ? raw.split(':')[0] : raw
                    const tail = raw.includes(':') ? raw.split(':').slice(1).join(':') : ''
                    return (
                        <div key={i} className="bg-white dark:bg-card-dark p-4 rounded-xl shadow-sm border border-amber-100 dark:border-amber-900/40">
                            <div className="flex items-center gap-2 mb-2 flex-wrap">
                                <span className="bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-200 text-xs font-bold px-2 py-1 rounded uppercase">
                                    Mnemonic
                                </span>
                                {m.effectiveness != null && (
                                    <span className="text-xs text-slate-400 dark:text-slate-500">Effectiveness: {m.effectiveness}</span>
                                )}
                            </div>
                            <p className="font-mono font-bold text-lg text-amber-900 dark:text-amber-100 mb-1">{head}</p>
                            <p className="text-sm text-slate-700 dark:text-slate-300 italic">
                                <MathText>{tail || raw}</MathText>
                            </p>
                            {m.concept != null && (
                                <div className="mt-3 pt-2 border-t border-amber-50 dark:border-amber-900/30">
                                    <p className="text-xs text-slate-500 dark:text-slate-400">
                                        <span className="font-bold text-amber-800 dark:text-amber-300">Concept:</span> {m.concept}
                                    </p>
                                </div>
                            )}
                        </div>
                    )
                })}
            </div>
        </Card>
    )
}

export const FlashcardsSection = ({ flashcards }) => {
    const items = flashcards || []
    if (!items.length) return null
    return (
        <Card className="p-6 border border-slate-200 dark:border-border-dark">
            <SectionHeader title="Flashcards" icon={<Lightbulb className="w-5 h-5 text-purple-500" />} />
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {items.map((fc, i) => (
                    <FlipCard key={i} card={fc} />
                ))}
            </div>
        </Card>
    )
}

export const RealWorldSection = ({ contexts }) => {
    const items = contexts || []
    if (!items.length) return null
    return (
        <Card className="p-6 border border-slate-200 dark:border-border-dark">
            <SectionHeader title="Real World Context" icon={<Factory className="w-5 h-5 text-slate-500" />} />
            <div className="space-y-4">
                {items.map((ctx, i) => (
                    <div key={i} className="text-sm rounded-lg border border-slate-100 dark:border-white/10 p-3">
                        <h5 className="font-bold text-slate-900 dark:text-white">{ctx.application}</h5>
                        <p className="text-slate-600 dark:text-slate-400 mb-2">{ctx.industry_example}</p>
                        {ctx.why_it_matters && (
                            <p className="text-xs text-blue-700 dark:text-blue-300 mt-2 bg-blue-50 dark:bg-blue-950/40 p-2 rounded">
                                <span className="font-bold">Why it matters:</span> {ctx.why_it_matters}
                            </p>
                        )}
                    </div>
                ))}
            </div>
        </Card>
    )
}

/** Full Tier 2 Deep Dive grid for QuestionDetail */
export const Tier2DeepDiveGrid = ({ tier2 }) => {
    if (!tier2) return null
    const mistakes = tier2.common_mistakes || []
    const mnemonics = tier2.mnemonics_memory_aids || []
    const flashcards = tier2.flashcards || []
    const realWorld = tier2.real_world_context || []
    const hasAnything =
        mistakes.length > 0 || mnemonics.length > 0 || flashcards.length > 0 || realWorld.length > 0 || tier2.exam_strategy
    if (!hasAnything) return null
    return (
        <div className="space-y-6 mt-2">
            <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wide text-primary">Deep Dive Viewer</span>
                <span className="h-px flex-1 bg-gradient-to-r from-primary/60 via-slate-200 to-transparent dark:via-white/10" />
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-6">
                    <CommonMistakesSection mistakes={mistakes} />
                    <ExamStrategyDetailSection examStrategy={tier2.exam_strategy} />
                </div>
                <div className="space-y-6">
                    <MnemonicsSection mnemonics={mnemonics} />
                    <FlashcardsSection flashcards={flashcards} />
                    <RealWorldSection contexts={realWorld} />
                </div>
            </div>
        </div>
    )
}
