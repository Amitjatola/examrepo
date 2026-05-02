import React from 'react'

/**
 * Vertical Q1…Qn navigator for playlist context or search-results navigation.
 */
const QuestionNavRail = ({
    questionIds,
    activeQuestionId,
    onSelectQuestionId,
    title = 'Questions',
}) => {
    if (!questionIds || questionIds.length <= 1) return null

    return (
        <nav
            className="hidden lg:flex flex-col w-14 shrink-0 border-r border-slate-200 dark:border-border-dark bg-white/80 dark:bg-card-dark/80 backdrop-blur-sm py-4 px-1 gap-1 overflow-y-auto max-h-[calc(100vh-8rem)] sticky top-24 self-start rounded-l-xl"
            aria-label="Question navigator"
        >
            <span className="text-[10px] font-bold uppercase text-center text-slate-400 dark:text-slate-500 px-0.5 mb-2 truncate">
                {title}
            </span>
            {questionIds.map((qid, idx) => {
                const active = qid === activeQuestionId
                return (
                    <button
                        key={`${qid}-${idx}`}
                        type="button"
                        onClick={() => onSelectQuestionId?.(qid)}
                        aria-current={active ? 'true' : undefined}
                        aria-label={`Go to question ${idx + 1}`}
                        className={`text-xs font-bold rounded-lg py-2 px-1 transition-colors cursor-pointer border ${
                            active
                                ? 'bg-primary text-white border-primary shadow-sm'
                                : 'bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-300 border-transparent hover:border-primary/40'
                        }`}
                    >
                        Q{idx + 1}
                    </button>
                )
            })}
        </nav>
    )
}

export default QuestionNavRail
