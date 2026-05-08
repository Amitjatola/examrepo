import React from 'react'
import { CalendarRange, Loader2 } from 'lucide-react'

const ctaLabelForAction = (action) => {
    switch (action) {
        case 'revision':
            return 'Open revision queue'
        case 'weakTopic':
            return 'Practice this topic'
        case 'pacing':
            return 'Practice with target time'
        case 'remediation':
            return 'Review mistakes'
        case 'mock':
            return 'Start mock'
        default:
            return 'Go'
    }
}

const WeeklyFocusPlanCard = ({
    blocks = [],
    loading = false,
    showEmpty = false,
    onOpenRevisionQueue,
    onPracticeWeakTopic,
    onOpenRemediationPlaylist,
    onRunMockPaper,
    onNavigateYear,
}) => {
    const handleBlockAction = (block) => {
        switch (block.action) {
            case 'revision':
                onOpenRevisionQueue?.()
                return
            case 'weakTopic':
            case 'pacing':
                if (block.topic) onPracticeWeakTopic?.(block.topic)
                return
            case 'remediation':
                onOpenRemediationPlaylist?.()
                return
            case 'mock':
                onRunMockPaper?.()
                return
            default:
                return
        }
    }

    const handleKeyDownBlock = (e, block) => {
        if (e.key !== 'Enter' && e.key !== ' ') return
        e.preventDefault()
        handleBlockAction(block)
    }

    return (
        <section
            aria-labelledby="weekly-focus-heading"
            className="rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] p-6 flex flex-col gap-4 shadow-sm"
        >
            <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="flex items-center gap-2 min-w-0">
                    <CalendarRange size={18} className="text-primary shrink-0" aria-hidden />
                    <h3 id="weekly-focus-heading" className="text-slate-900 dark:text-white font-semibold">
                        This week&apos;s focus
                    </h3>
                </div>
            </div>
            <p className="text-xs text-slate-500 dark:text-text-muted leading-relaxed">
                A simple prioritized list from your heatmap, mistakes, and revision queue — not a full timetable.
            </p>

            {loading ? (
                <div className="flex justify-center py-8" role="status" aria-live="polite">
                    <Loader2 size={22} className="animate-spin text-slate-400" aria-hidden />
                    <span className="sr-only">Loading focus plan</span>
                </div>
            ) : showEmpty ? (
                <div className="rounded-lg border border-dashed border-slate-200 dark:border-white/15 bg-slate-50/80 dark:bg-white/5 p-5 flex flex-col gap-3">
                    <p className="text-sm text-slate-600 dark:text-slate-300">
                        Attempt questions to get a tailored focus plan from your accuracy and timing.
                    </p>
                    <button
                        type="button"
                        onClick={() => onNavigateYear?.()}
                        className="self-start inline-flex items-center justify-center rounded-lg bg-primary hover:bg-blue-600 text-white text-sm font-bold px-4 py-2.5 cursor-pointer"
                    >
                        Quick practice
                    </button>
                </div>
            ) : (
                <ol className="flex flex-col gap-3 list-decimal list-inside marker:font-bold marker:text-slate-400" aria-label="Weekly focus steps">
                    {blocks.map((block) => (
                        <li key={block.id} className="rounded-lg border border-slate-100 dark:border-white/10 bg-slate-50/90 dark:bg-white/5 p-4">
                            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                                <div className="min-w-0 space-y-1 pl-1">
                                    <p className="text-sm font-bold text-slate-900 dark:text-white">{block.title}</p>
                                    <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{block.reason}</p>
                                </div>
                                <button
                                    type="button"
                                    tabIndex={0}
                                    aria-label={`${ctaLabelForAction(block.action)}: ${block.title}`}
                                    onClick={() => handleBlockAction(block)}
                                    onKeyDown={(e) => handleKeyDownBlock(e, block)}
                                    className="shrink-0 inline-flex items-center justify-center rounded-lg bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-3 py-2 text-xs font-bold hover:opacity-90 cursor-pointer"
                                >
                                    {ctaLabelForAction(block.action)}
                                </button>
                            </div>
                        </li>
                    ))}
                </ol>
            )}

            <p className="text-[11px] text-slate-400 dark:text-slate-500 border-t border-slate-100 dark:border-white/10 pt-3">
                Suggestions from your recent practice; adjust anytime.
            </p>
        </section>
    )
}

export default WeeklyFocusPlanCard
