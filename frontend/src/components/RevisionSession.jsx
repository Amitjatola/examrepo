import React, { useCallback, useEffect, useState } from 'react'
import { ArrowLeft, Eye, Loader2 } from 'lucide-react'
import { api } from '../utils/api'
import LatexRenderer from './LatexRenderer'

const RevisionSession = ({ questionIds, onBack }) => {
    const [index, setIndex] = useState(0)
    const [question, setQuestion] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [revealed, setRevealed] = useState(false)
    const [busy, setBusy] = useState(false)
    const [doneStats, setDoneStats] = useState(null)
    const [reviewedCount, setReviewedCount] = useState(0)

    const ids = Array.isArray(questionIds) ? questionIds.filter(Boolean) : []
    const currentId = ids[index] || null
    const isComplete = index >= ids.length

    const loadQuestion = useCallback(async (qid) => {
        if (!qid) return
        setLoading(true)
        setError(null)
        setRevealed(false)
        try {
            const q = await api.get(`/questions/${qid}`)
            setQuestion(q)
        } catch (e) {
            setError(e?.message || 'Failed to load question')
            setQuestion(null)
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        if (!currentId) {
            setLoading(false)
            return undefined
        }
        loadQuestion(currentId)
        return undefined
    }, [currentId, loadQuestion])

    const handleReveal = () => {
        setRevealed(true)
    }

    const handleRate = async (quality) => {
        if (!currentId || busy) return
        setBusy(true)
        setError(null)
        try {
            await api.answerRevision(currentId, quality)
            setReviewedCount((c) => c + 1)
            const next = index + 1
            if (next >= ids.length) {
                const stats = await api.getRevisionStats().catch(() => null)
                setDoneStats(stats)
            }
            setIndex(next)
        } catch (e) {
            setError(e?.message || 'Could not save review')
        } finally {
            setBusy(false)
        }
    }

    if (!ids.length) {
        return (
            <div className="flex-1 flex items-center justify-center p-8 text-slate-600 dark:text-gray-400">
                <p>No questions in this session.</p>
            </div>
        )
    }

    if (isComplete) {
        return (
            <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark min-h-full flex items-center justify-center p-6">
                <div className="max-w-md w-full rounded-2xl border border-slate-200 dark:border-border-dark bg-white dark:bg-card-dark p-8 text-center space-y-4 shadow-sm">
                    <h2 className="text-2xl font-black text-slate-900 dark:text-white font-display">Session complete</h2>
                    <p className="text-slate-600 dark:text-gray-400 text-sm">
                        You reviewed <span className="font-bold text-slate-900 dark:text-white">{reviewedCount}</span> question
                        {reviewedCount === 1 ? '' : 's'}.
                    </p>
                    {doneStats ? (
                        <p className="text-sm text-slate-500 dark:text-gray-400">
                            Revision streak:{' '}
                            <span className="font-bold text-primary">{doneStats.current_streak}</span> days · Still due:{' '}
                            <span className="font-bold text-slate-900 dark:text-white">{doneStats.due_today}</span>
                        </p>
                    ) : null}
                    <button
                        type="button"
                        onClick={() => onBack?.()}
                        className="w-full rounded-lg bg-primary hover:bg-blue-600 text-white font-bold py-3 cursor-pointer"
                    >
                        Back to queue
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark min-h-full">
            <div className="max-w-[49.28rem] mx-auto p-4 md:p-8 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                    <button
                        type="button"
                        onClick={() => onBack?.()}
                        className="inline-flex items-center gap-2 text-slate-600 dark:text-gray-400 hover:text-primary cursor-pointer"
                    >
                        <ArrowLeft size={20} />
                        <span className="text-sm font-semibold">Exit session</span>
                    </button>
                    <p className="text-xs font-semibold text-slate-500 dark:text-gray-400">
                        {index + 1} / {ids.length}
                    </p>
                </div>
                {error ? (
                    <div className="rounded-lg border border-red-200 dark:border-red-900/40 bg-red-50 dark:bg-red-950/30 px-4 py-3 text-sm text-red-700 dark:text-red-300">
                        {error}
                    </div>
                ) : null}

                {loading ? (
                    <div className="flex justify-center py-20">
                        <Loader2 className="animate-spin w-10 h-10 text-slate-400" aria-label="Loading question" />
                    </div>
                ) : !question ? (
                    <p className="text-center text-slate-500">Question not found.</p>
                ) : (
                    <div className="rounded-xl border border-[#e5e7eb] dark:border-border-dark bg-white dark:bg-card-dark overflow-hidden shadow-sm">
                        <div className="px-5 py-4 border-b border-[#f0f2f4] dark:border-border-dark">
                            <h2 className="text-lg font-bold text-slate-900 dark:text-white">{question.question_id}</h2>
                            <p className="text-xs text-slate-500 dark:text-gray-400 mt-1">
                                {question.question_type} · {question.marks} marks · Q{question.question_number}
                            </p>
                        </div>
                        <div className="px-5 py-4 text-slate-900 dark:text-gray-200 text-base leading-relaxed">
                            <LatexRenderer
                                text={question.question_text_latex || question.question_text || '—'}
                            />
                        </div>
                        {question.options && typeof question.options === 'object' && !Array.isArray(question.options) ? (
                            <div className="px-5 pb-4 space-y-2">
                                {Object.entries(question.options).map(([key, value]) => (
                                    <div
                                        key={key}
                                        className="flex gap-3 rounded-lg border border-[#e5e7eb] dark:border-border-dark px-3 py-2 bg-slate-50/80 dark:bg-white/5"
                                    >
                                        <span className="font-bold text-primary">{key}</span>
                                        <div className="text-sm">
                                            <LatexRenderer text={value} />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : null}

                        {!revealed ? (
                            <div className="px-5 py-4 bg-gray-50 dark:bg-landing-bg-dark/30 border-t border-[#e5e7eb] dark:border-border-dark flex flex-wrap gap-2">
                                <button
                                    type="button"
                                    onClick={handleReveal}
                                    className="inline-flex items-center gap-2 rounded-lg bg-white dark:bg-card-dark border border-[#e5e7eb] dark:border-border-dark px-4 py-2 text-sm font-semibold text-slate-900 dark:text-white hover:bg-slate-50 dark:hover:bg-white/10 cursor-pointer"
                                >
                                    <Eye size={16} />
                                    Reveal answer
                                </button>
                            </div>
                        ) : (
                            <div className="px-5 py-4 space-y-4 border-t border-[#e5e7eb] dark:border-border-dark bg-blue-50/40 dark:bg-blue-950/20">
                                <p className="text-sm font-bold text-slate-900 dark:text-white">
                                    Correct answer:{' '}
                                    <span className="text-primary">{question.answer_key}</span>
                                </p>
                                <p className="text-xs text-slate-500 dark:text-gray-400 font-semibold uppercase tracking-wide">
                                    How well did you recall?
                                </p>
                                <div className="flex flex-wrap gap-2">
                                    {[
                                        { q: 'again', label: 'Again', cls: 'bg-red-600 hover:bg-red-700 text-white' },
                                        { q: 'hard', label: 'Hard', cls: 'bg-orange-500 hover:bg-orange-600 text-white' },
                                        { q: 'good', label: 'Good', cls: 'bg-emerald-600 hover:bg-emerald-700 text-white' },
                                        { q: 'easy', label: 'Easy', cls: 'bg-blue-600 hover:bg-blue-700 text-white' },
                                    ].map((b) => (
                                        <button
                                            key={b.q}
                                            type="button"
                                            disabled={busy}
                                            onClick={() => handleRate(b.q)}
                                            className={`px-4 py-2 rounded-lg text-sm font-bold transition-opacity cursor-pointer disabled:opacity-50 ${b.cls}`}
                                        >
                                            {busy ? 'Saving…' : b.label}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}

export default RevisionSession
