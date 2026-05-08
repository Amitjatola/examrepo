import React, { useCallback, useEffect, useState } from 'react'
import {
    MessageSquare,
    ThumbsUp,
    ThumbsDown,
    Trash2,
    Loader2,
} from 'lucide-react'
import { api } from '../utils/api'
import { useAuth } from '../context/AuthContext'

const formatRelativeTime = (iso) => {
    if (!iso) return ''
    const then = new Date(iso).getTime()
    const sec = Math.floor((Date.now() - then) / 1000)
    if (sec < 60) return 'just now'
    const min = Math.floor(sec / 60)
    if (min < 60) return `${min}m ago`
    const hr = Math.floor(min / 60)
    if (hr < 24) return `${hr}h ago`
    const day = Math.floor(hr / 24)
    if (day < 7) return `${day}d ago`
    return new Date(iso).toLocaleDateString()
}

const avatarLetter = (comment, fallbackEmail) => {
    const name = comment?.user_name || ''
    const email = comment?.user_email || ''
    const ch = (name.trim()[0] || email.trim()[0] || fallbackEmail?.[0] || '?').toUpperCase()
    return ch
}

const displayAuthor = (comment) => {
    if (comment?.user_name?.trim()) return comment.user_name.trim()
    if (comment?.user_email) return comment.user_email.split('@')[0]
    return 'User'
}

/**
 * @param {{ questionId?: string }} props — internal question UUID from API (`question.id`)
 */
const DiscussionSection = ({ questionId }) => {
    const { user, openLogin } = useAuth()
    const [comments, setComments] = useState([])
    const [loading, setLoading] = useState(false)
    const [posting, setPosting] = useState(false)
    const [draft, setDraft] = useState('')
    const [error, setError] = useState(null)
    const [voteBusyId, setVoteBusyId] = useState(null)
    const [showGuidelines, setShowGuidelines] = useState(false)

    const loadComments = useCallback(async () => {
        if (!questionId) return
        setLoading(true)
        setError(null)
        try {
            const list = await api.getDiscussions(questionId)
            setComments(Array.isArray(list) ? list : [])
        } catch (e) {
            setError(e?.message || 'Could not load discussion')
            setComments([])
        } finally {
            setLoading(false)
        }
    }, [questionId])

    useEffect(() => {
        loadComments()
    }, [loadComments])

    const handlePostComment = async () => {
        const text = draft.trim()
        if (!text || !questionId || !user) return
        setPosting(true)
        setError(null)
        try {
            const created = await api.postDiscussion(questionId, text, null)
            setDraft('')
            setComments((prev) => [created, ...prev])
        } catch (e) {
            setError(e?.message || 'Could not post comment')
        } finally {
            setPosting(false)
        }
    }

    const handleVote = async (discussionId, voteType) => {
        if (!user) {
            openLogin?.()
            return
        }
        setVoteBusyId(discussionId)
        setError(null)
        try {
            const updated = await api.voteDiscussion(discussionId, voteType)
            setComments((prev) =>
                prev.map((c) => (String(c.id) === String(updated.id) ? updated : c)),
            )
        } catch (e) {
            setError(e?.message || 'Vote failed')
        } finally {
            setVoteBusyId(null)
        }
    }

    const handleDelete = async (discussionId) => {
        if (!user) return
        setError(null)
        try {
            await api.deleteDiscussion(discussionId)
            setComments((prev) => prev.filter((c) => String(c.id) !== String(discussionId)))
        } catch (e) {
            setError(e?.message || 'Could not delete comment')
        }
    }

    const handleToggleGuidelines = () => {
        setShowGuidelines((v) => !v)
    }

    const handleDraftKeyDown = (e) => {
        if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
            e.preventDefault()
            handlePostComment()
        }
    }

    if (!questionId) return null

    const countLabel =
        comments.length === 1 ? '1 Comment' : `${comments.length} Comments`

    return (
        <section
            className="rounded-xl border border-[#e5e7eb] dark:border-border-dark bg-white dark:bg-card-dark shadow-sm overflow-hidden"
            aria-labelledby="discussion-heading"
        >
            <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-4 border-b border-[#f0f2f4] dark:border-border-dark">
                <div className="flex flex-wrap items-center gap-3 min-w-0">
                    <MessageSquare className="w-5 h-5 text-slate-500 dark:text-gray-400 shrink-0" aria-hidden />
                    <h3
                        id="discussion-heading"
                        className="text-base font-bold text-slate-900 dark:text-white"
                    >
                        Discussion
                    </h3>
                    <span className="inline-flex items-center rounded-full bg-[#f0f2f4] dark:bg-background-dark/60 px-2.5 py-0.5 text-xs font-semibold text-[#617589] dark:text-gray-400">
                        {countLabel}
                    </span>
                </div>
                <button
                    type="button"
                    onClick={handleToggleGuidelines}
                    className="text-sm font-semibold text-primary hover:text-blue-600 dark:hover:text-blue-400 shrink-0 cursor-pointer"
                    aria-expanded={showGuidelines}
                    aria-controls="discussion-guidelines-panel"
                >
                    Guidelines
                </button>
            </div>

            {showGuidelines && (
                <div
                    id="discussion-guidelines-panel"
                    className="px-5 py-3 bg-slate-50 dark:bg-white/5 border-b border-[#f0f2f4] dark:border-border-dark text-sm text-slate-600 dark:text-gray-300 space-y-2"
                    role="region"
                    aria-label="Discussion guidelines"
                >
                    <p className="font-semibold text-slate-800 dark:text-white text-xs uppercase tracking-wide">
                        Quick guidelines
                    </p>
                    <ul className="list-disc pl-5 space-y-1">
                        <li>Stay respectful and on-topic for this question.</li>
                        <li>No spam, hate, or exam-cheating solicitations.</li>
                    </ul>
                </div>
            )}

            {error && (
                <div className="mx-5 mt-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-900/40 px-4 py-2 text-sm text-red-700 dark:text-red-300">
                    {error}
                </div>
            )}

            {user ? (
                <div className="p-5 flex gap-4 border-b border-[#f0f2f4] dark:border-border-dark">
                    <div
                        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-white text-sm font-bold"
                        aria-hidden
                    >
                        {avatarLetter(
                            { user_name: user.full_name, user_email: user.email },
                            user.email,
                        )}
                    </div>
                    <div className="flex-1 min-w-0 space-y-3">
                        <label htmlFor="discussion-draft" className="sr-only">
                            Add to the discussion
                        </label>
                        <textarea
                            id="discussion-draft"
                            value={draft}
                            onChange={(e) => setDraft(e.target.value)}
                            onKeyDown={handleDraftKeyDown}
                            placeholder="Add to the discussion..."
                            rows={4}
                            className="w-full rounded-lg border border-slate-200 dark:border-border-dark bg-slate-50 dark:bg-[#1a1d2e] px-4 py-3 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-gray-500 focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none resize-y min-h-[100px]"
                            disabled={posting}
                            aria-label="Add to the discussion"
                        />
                        <div className="flex flex-wrap items-center justify-end gap-3">
                            <button
                                type="button"
                                onClick={handlePostComment}
                                disabled={posting || !draft.trim()}
                                className="inline-flex items-center gap-2 rounded-lg bg-primary hover:bg-blue-600 disabled:bg-gray-300 dark:disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed text-white text-sm font-semibold px-5 py-2.5 shadow-sm transition-colors cursor-pointer"
                            >
                                {posting ? (
                                    <>
                                        <Loader2 className="animate-spin" size={16} aria-hidden />
                                        Posting…
                                    </>
                                ) : (
                                    'Post Comment'
                                )}
                            </button>
                        </div>
                        <p className="text-[11px] text-slate-400 dark:text-gray-500">
                            Tip: ⌘Enter / Ctrl+Enter to post
                        </p>
                    </div>
                </div>
            ) : (
                <div className="p-6 text-center border-b border-[#f0f2f4] dark:border-border-dark bg-slate-50/80 dark:bg-white/5">
                    <p className="text-sm text-slate-600 dark:text-gray-300 mb-4">
                        Sign in to join the discussion.
                    </p>
                    <button
                        type="button"
                        onClick={() => openLogin?.()}
                        className="rounded-lg bg-primary hover:bg-blue-600 text-white text-sm font-semibold px-6 py-2.5 shadow-sm transition-colors cursor-pointer"
                    >
                        Sign in
                    </button>
                </div>
            )}

            <div className="p-5">
                {loading ? (
                    <div className="flex justify-center py-10 text-slate-500 dark:text-gray-400">
                        <Loader2 className="animate-spin w-8 h-8" aria-label="Loading comments" />
                    </div>
                ) : comments.length === 0 ? (
                    <p className="text-center text-sm text-slate-500 dark:text-gray-400 py-8">
                        No comments yet. Be the first to discuss!
                    </p>
                ) : (
                    <ul className="space-y-6">
                        {comments.map((c) => {
                            const own =
                                user?.email &&
                                c.user_email &&
                                user.email.toLowerCase() === String(c.user_email).toLowerCase()
                            const busy = voteBusyId === String(c.id)
                            return (
                                <li
                                    key={c.id}
                                    className="flex gap-4 pb-6 border-b border-[#f0f2f4] dark:border-border-dark last:border-0 last:pb-0"
                                >
                                    <div
                                        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-slate-200 dark:bg-[#2f396a] text-slate-700 dark:text-white text-sm font-bold"
                                        aria-hidden
                                    >
                                        {avatarLetter(c, user?.email)}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1 mb-1">
                                            <span className="font-semibold text-slate-900 dark:text-white text-sm">
                                                {displayAuthor(c)}
                                            </span>
                                            <span className="text-xs text-slate-400 dark:text-gray-500">
                                                {formatRelativeTime(c.created_at)}
                                            </span>
                                        </div>
                                        <p className="text-sm text-slate-700 dark:text-gray-200 whitespace-pre-wrap break-words mb-3">
                                            {c.content}
                                        </p>
                                        <div className="flex flex-wrap items-center gap-2">
                                            <button
                                                type="button"
                                                onClick={() => handleVote(c.id, 'upvote')}
                                                disabled={busy}
                                                className="inline-flex items-center gap-1 rounded-lg border border-slate-200 dark:border-border-dark px-2 py-1 text-xs font-medium text-slate-600 dark:text-gray-300 hover:bg-slate-50 dark:hover:bg-white/10 disabled:opacity-50 cursor-pointer"
                                                aria-label={`Upvote comment`}
                                            >
                                                <ThumbsUp size={14} aria-hidden />
                                                {c.upvotes ?? 0}
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => handleVote(c.id, 'downvote')}
                                                disabled={busy}
                                                className="inline-flex items-center gap-1 rounded-lg border border-slate-200 dark:border-border-dark px-2 py-1 text-xs font-medium text-slate-600 dark:text-gray-300 hover:bg-slate-50 dark:hover:bg-white/10 disabled:opacity-50 cursor-pointer"
                                                aria-label={`Downvote comment`}
                                            >
                                                <ThumbsDown size={14} aria-hidden />
                                                {c.downvotes ?? 0}
                                            </button>
                                            {own && (
                                                <button
                                                    type="button"
                                                    onClick={() => handleDelete(c.id)}
                                                    className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 cursor-pointer"
                                                    aria-label="Delete your comment"
                                                >
                                                    <Trash2 size={14} aria-hidden />
                                                    Delete
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </li>
                            )
                        })}
                    </ul>
                )}
            </div>
        </section>
    )
}

export default DiscussionSection
