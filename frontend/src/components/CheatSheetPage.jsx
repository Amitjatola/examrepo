import React, { useCallback, useEffect, useState } from 'react'
import { FileText, Loader2, Printer, ArrowLeft } from 'lucide-react'
import { api } from '../utils/api'
import LatexRenderer from './LatexRenderer'
import { extractFormulaBlocksFromTier1, formulaBlockDedupeKey } from '../utils/formulaBlocks'

/**
 * @param {object} question
 * @returns {string}
 */
const topicFromQuestion = (question) => {
    const t1 = question?.tier_1_core_research
    const tags = t1?.hierarchical_tags
    const name = tags?.topic?.name
    return typeof name === 'string' && name.trim() ? name.trim() : 'General'
}

const CheatSheetPage = ({ user, openLogin, onBack }) => {
    const [filterSubjects, setFilterSubjects] = useState([])
    const [filterSubject, setFilterSubject] = useState('')
    const [filterTopic, setFilterTopic] = useState('')
    const [includeBookmarks, setIncludeBookmarks] = useState(true)
    const [includeRemediation, setIncludeRemediation] = useState(true)
    const [includeRevision, setIncludeRevision] = useState(true)
    const [includeFilterSearch, setIncludeFilterSearch] = useState(false)

    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    /** @type {Record<string, Record<string, { title: string, body: string, sourceQuestionId: string }[]>>} */
    const [grouped, setGrouped] = useState({})
    const [stats, setStats] = useState({ questionCount: 0, blockCount: 0 })

    useEffect(() => {
        const handleBeforePrint = () => {
            document.body.classList.add('cheatsheet-print-mode')
        }
        const handleAfterPrint = () => {
            document.body.classList.remove('cheatsheet-print-mode')
        }
        window.addEventListener('beforeprint', handleBeforePrint)
        window.addEventListener('afterprint', handleAfterPrint)
        return () => {
            window.removeEventListener('beforeprint', handleBeforePrint)
            window.removeEventListener('afterprint', handleAfterPrint)
            document.body.classList.remove('cheatsheet-print-mode')
        }
    }, [])

    useEffect(() => {
        let cancelled = false
        ;(async () => {
            try {
                const fo = await api.get('/search/filters')
                if (!cancelled && fo?.subjects) setFilterSubjects(Array.isArray(fo.subjects) ? fo.subjects : [])
            } catch {
                if (!cancelled) setFilterSubjects([])
            }
        })()
        return () => {
            cancelled = true
        }
    }, [])

    const handleGenerate = useCallback(async () => {
        setError(null)
        setLoading(true)
        setGrouped({})

        const idSet = new Set()

        try {
            if (user && includeBookmarks) {
                try {
                    const marks = await api.get('/users/me/bookmarks', { limit: 200 })
                    ;(Array.isArray(marks) ? marks : []).forEach((b) => {
                        if (b?.question_id) idSet.add(b.question_id)
                    })
                } catch {
                    /* skip */
                }
            }

            if (user && includeRemediation) {
                try {
                    const rem = await api.get('/dashboard/remediation', { limit: 100 })
                    ;(rem.items || []).forEach((i) => {
                        if (i?.question_id) idSet.add(i.question_id)
                    })
                } catch {
                    /* skip */
                }
            }

            if (user && includeRevision) {
                try {
                    const q = await api.getRevisionQueue({ limit: 80 })
                    ;(q.items || []).forEach((row) => {
                        const id = row?.revision?.question_id_str
                        if (id) idSet.add(id)
                    })
                } catch {
                    /* skip */
                }
            }

            if (includeFilterSearch && (filterSubject || filterTopic)) {
                const params = { q: '', page_size: 80 }
                if (filterSubject) params.subject = filterSubject
                if (filterTopic.trim()) params.topic = filterTopic.trim()
                const data = await api.get('/search', params)
                ;(data.questions || []).forEach((q) => {
                    if (q?.question_id) idSet.add(q.question_id)
                })
            }

            const ids = [...idSet]
            if (ids.length === 0) {
                setStats({ questionCount: 0, blockCount: 0 })
                setLoading(false)
                return
            }

            const questions = await api.getQuestionsByIds(ids)

            const seenKeys = new Set()
            /** @type {Record<string, Record<string, { title: string, body: string, sourceQuestionId: string }[]>>} */
            const next = {}
            let blockCount = 0

            for (const q of questions) {
                const subject = q?.subject || 'Unknown subject'
                const topic = topicFromQuestion(q)
                const blocks = extractFormulaBlocksFromTier1(q?.tier_1_core_research || {})

                for (const b of blocks) {
                    const dk = formulaBlockDedupeKey(b.title, b.body)
                    if (seenKeys.has(dk)) continue
                    seenKeys.add(dk)
                    if (!next[subject]) next[subject] = {}
                    if (!next[subject][topic]) next[subject][topic] = []
                    next[subject][topic].push({
                        title: b.title,
                        body: b.body,
                        sourceQuestionId: q.question_id,
                    })
                    blockCount += 1
                }
            }

            setGrouped(next)
            setStats({ questionCount: questions.length, blockCount })
        } catch (e) {
            setError(e?.message || 'Could not build cheat sheet.')
            setGrouped({})
            setStats({ questionCount: 0, blockCount: 0 })
        } finally {
            setLoading(false)
        }
    }, [
        user,
        includeBookmarks,
        includeRemediation,
        includeRevision,
        includeFilterSearch,
        filterSubject,
        filterTopic,
    ])

    useEffect(() => {
        void handleGenerate()
        // eslint-disable-next-line react-hooks/exhaustive-deps -- manual "Refresh sheet" applies other control changes
    }, [user])

    const handlePrint = () => {
        window.print()
    }

    const subjectsSorted = Object.keys(grouped).sort((a, b) => a.localeCompare(b))

    return (
        <div className="flex flex-col h-full min-h-0 overflow-y-auto bg-background-light dark:bg-background-dark">
            <div className="no-print max-w-4xl mx-auto w-full px-4 py-6 space-y-6">
                <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-2 min-w-0">
                        <FileText size={22} className="text-primary shrink-0" aria-hidden />
                        <h1 className="text-2xl font-bold text-slate-900 dark:text-white truncate">Formula cheat sheet</h1>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        <button
                            type="button"
                            onClick={() => onBack?.()}
                            className="inline-flex items-center gap-2 rounded-lg border border-slate-200 dark:border-border-dark px-3 py-2 text-sm font-semibold text-slate-800 dark:text-slate-100 hover:bg-slate-50 dark:hover:bg-white/5 cursor-pointer"
                        >
                            <ArrowLeft size={16} aria-hidden />
                            Back
                        </button>
                        <button
                            type="button"
                            onClick={handlePrint}
                            className="inline-flex items-center gap-2 rounded-lg bg-primary text-white px-3 py-2 text-sm font-bold hover:bg-blue-600 cursor-pointer"
                        >
                            <Printer size={16} aria-hidden />
                            Print / Save as PDF
                        </button>
                    </div>
                </div>

                {!user ? (
                    <div className="rounded-xl border border-amber-200 dark:border-amber-900/50 bg-amber-50/90 dark:bg-amber-950/30 p-4 text-sm text-amber-950 dark:text-amber-100">
                        Sign in to include bookmarks, mistakes, and revision queue. You can still use subject/topic filters
                        below.
                        <button
                            type="button"
                            onClick={() => openLogin?.()}
                            className="ml-2 font-bold text-primary hover:underline cursor-pointer"
                        >
                            Sign in
                        </button>
                    </div>
                ) : null}

                <div className="rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] p-4 space-y-4">
                    <p className="text-xs text-slate-500 dark:text-text-muted leading-relaxed">
                        Choose sources and filters, then refresh. Content comes from each question&apos;s tier-1 formulas and
                        principles field.
                    </p>
                    <fieldset className="space-y-2 border-0 p-0 m-0">
                        <legend className="text-xs font-bold text-slate-500 dark:text-slate-400 sr-only">Sources</legend>
                        {user ? (
                            <div className="flex flex-col sm:flex-row flex-wrap gap-3 text-sm">
                                <label className="inline-flex items-center gap-2 cursor-pointer text-slate-800 dark:text-slate-200">
                                    <input
                                        type="checkbox"
                                        checked={includeBookmarks}
                                        onChange={(e) => setIncludeBookmarks(e.target.checked)}
                                    />
                                    Bookmarks
                                </label>
                                <label className="inline-flex items-center gap-2 cursor-pointer text-slate-800 dark:text-slate-200">
                                    <input
                                        type="checkbox"
                                        checked={includeRemediation}
                                        onChange={(e) => setIncludeRemediation(e.target.checked)}
                                    />
                                    Recent mistakes
                                </label>
                                <label className="inline-flex items-center gap-2 cursor-pointer text-slate-800 dark:text-slate-200">
                                    <input
                                        type="checkbox"
                                        checked={includeRevision}
                                        onChange={(e) => setIncludeRevision(e.target.checked)}
                                    />
                                    Revision queue
                                </label>
                            </div>
                        ) : (
                            <p className="text-xs text-slate-500">Sign in to enable bookmark, mistake, and revision sources.</p>
                        )}
                    </fieldset>

                    <div className="flex flex-col sm:flex-row flex-wrap gap-3 items-start">
                        <label className="flex flex-col text-xs font-semibold text-slate-500 gap-1 min-w-[180px]">
                            Filter: subject
                            <select
                                value={filterSubject}
                                onChange={(e) => setFilterSubject(e.target.value)}
                                className="rounded-lg border border-slate-200 dark:border-border-dark bg-white dark:bg-[#1a1d2e] text-sm px-2 py-2 text-slate-900 dark:text-white"
                            >
                                <option value="">Any</option>
                                {filterSubjects.map((s) => (
                                    <option key={s} value={s}>
                                        {s}
                                    </option>
                                ))}
                            </select>
                        </label>
                        <label className="flex flex-col text-xs font-semibold text-slate-500 gap-1 flex-1 min-w-[160px]">
                            Filter: topic (optional)
                            <input
                                type="text"
                                value={filterTopic}
                                onChange={(e) => setFilterTopic(e.target.value)}
                                placeholder="Exact topic name"
                                className="rounded-lg border border-slate-200 dark:border-border-dark bg-white dark:bg-[#1a1d2e] text-sm px-2 py-2 text-slate-900 dark:text-white"
                            />
                        </label>
                        <label className="inline-flex items-center gap-2 text-sm text-slate-800 dark:text-slate-200 mt-6 sm:mt-0 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={includeFilterSearch}
                                onChange={(e) => setIncludeFilterSearch(e.target.checked)}
                            />
                            Include filter results
                        </label>
                    </div>

                    <button
                        type="button"
                        onClick={handleGenerate}
                        disabled={loading}
                        className="inline-flex items-center gap-2 rounded-lg bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-4 py-2 text-sm font-semibold hover:opacity-90 disabled:opacity-50 cursor-pointer"
                    >
                        {loading ? <Loader2 size={16} className="animate-spin" aria-hidden /> : null}
                        Refresh sheet
                    </button>
                </div>

                {error ? (
                    <p className="text-sm text-red-600 dark:text-red-400" role="alert">
                        {error}
                    </p>
                ) : null}

                {!loading && stats.blockCount === 0 ? (
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                        No formula blocks found for the current selection. Try enabling more sources, add bookmarks, or widen
                        filters (max 200 questions per build).
                    </p>
                ) : null}

                {!loading && stats.blockCount > 0 ? (
                    <p className="no-print text-xs text-slate-500">
                        {stats.blockCount} unique block{stats.blockCount === 1 ? '' : 's'} from {stats.questionCount}{' '}
                        question{stats.questionCount === 1 ? '' : 's'} (deduped).
                    </p>
                ) : null}
            </div>

            <div className="cheatsheet-print-root max-w-4xl mx-auto w-full px-4 pb-10 space-y-8">
                <div className="rounded-lg border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/5 p-4 text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                    <strong className="text-slate-800 dark:text-slate-200">Disclaimer:</strong> This sheet is a study aid
                    aggregated from app content. It may not be exhaustive, may contain errors, and is not a substitute for
                    official syllabi or textbooks. Verify critical material independently.
                </div>

                {loading ? (
                    <div className="flex justify-center py-12 no-print" role="status">
                        <Loader2 size={28} className="animate-spin text-slate-400" aria-hidden />
                        <span className="sr-only">Loading cheat sheet</span>
                    </div>
                ) : null}

                {subjectsSorted.map((subject) => (
                    <section key={subject} className="cheatsheet-subject space-y-4">
                        <h2 className="text-xl font-bold text-slate-900 dark:text-white border-b border-slate-200 dark:border-white/10 pb-2 cheatsheet-subject-title">
                            {subject}
                        </h2>
                        {Object.keys(grouped[subject] || {})
                            .sort((a, b) => a.localeCompare(b))
                            .map((topic) => (
                                <div key={`${subject}-${topic}`} className="space-y-3">
                                    <h3 className="text-sm font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                                        {topic}
                                    </h3>
                                    <div className="space-y-3">
                                        {(grouped[subject][topic] || []).map((row, idx) => (
                                            <article
                                                key={`${row.sourceQuestionId}-${idx}`}
                                                className="cheatsheet-formula-card rounded-xl border border-slate-100 dark:border-white/10 bg-white dark:bg-[#15192b] p-4"
                                            >
                                                <h4 className="text-sm font-bold text-slate-900 dark:text-white mb-2">
                                                    {row.title}
                                                </h4>
                                                <div className="text-slate-800 dark:text-slate-200 text-base leading-relaxed">
                                                    <LatexRenderer text={row.body} />
                                                </div>
                                                <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-2 font-mono">
                                                    Source: {row.sourceQuestionId}
                                                </p>
                                            </article>
                                        ))}
                                    </div>
                                </div>
                            ))}
                    </section>
                ))}
            </div>
        </div>
    )
}

export default CheatSheetPage
