import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import LatexRenderer from './LatexRenderer';
import { MessageSquare, ThumbsUp, ThumbsDown, Trash2, Reply, Send, Loader2, LogIn } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const DiscussionSection = ({ questionId }) => {
    const [discussions, setDiscussions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [newComment, setNewComment] = useState("");
    const [replyTo, setReplyTo] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const { user, requireAuth } = useAuth();

    useEffect(() => {
        fetchDiscussions();
    }, [questionId]);

    const fetchDiscussions = async () => {
        try {
            setLoading(true);
            const data = await api.getDiscussions(questionId);
            setDiscussions(data);
            setError(null);
        } catch (err) {
            console.error("Failed to fetch discussions:", err);
            setError("Failed to load discussions. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handlePost = async (parentId = null) => {
        if (!newComment.trim()) return;

        // Gate: require login to post
        if (!requireAuth("Sign in to join the discussion")) return;

        try {
            setSubmitting(true);
            const freshComment = await api.postDiscussion(questionId, newComment, parentId);

            if (!parentId) {
                setDiscussions([freshComment, ...discussions]);
            } else {
                await fetchDiscussions();
            }

            setNewComment("");
            setReplyTo(null);
        } catch (err) {
            console.error("Failed to post comment:", err);
            alert("Failed to post comment.");
        } finally {
            setSubmitting(false);
        }
    };

    const handleVote = async (discussionId, voteType) => {
        // Gate: require login to vote
        if (!requireAuth("Sign in to vote on discussions")) return;

        try {
            const updatedDiscussion = await api.voteDiscussion(discussionId, voteType);

            setDiscussions(prev => prev.map(d =>
                d.id === discussionId ? updatedDiscussion : d
            ));
        } catch (err) {
            console.error("Failed to vote:", err);
        }
    };

    const handleDelete = async (discussionId) => {
        if (!window.confirm("Are you sure you want to delete this comment?")) return;

        try {
            await api.deleteDiscussion(discussionId);
            setDiscussions(prev => prev.filter(d => d.id !== discussionId));
        } catch (err) {
            console.error("Failed to delete:", err);
            alert("Failed to delete comment.");
        }
    };

    const buildTree = (comments) => {
        const map = {};
        const roots = [];

        comments.forEach(c => {
            map[c.id] = { ...c, children: [] };
        });

        comments.forEach(c => {
            if (c.parent_id && map[c.parent_id]) {
                map[c.parent_id].children.push(map[c.id]);
            } else {
                roots.push(map[c.id]);
            }
        });

        return roots.sort((a, b) => b.upvotes - a.upvotes || new Date(b.created_at) - new Date(a.created_at));
    };

    const commentTree = buildTree(discussions);

    const CommentItem = ({ comment, depth = 0 }) => {
        const [isReplying, setIsReplying] = useState(false);
        const [replyText, setReplyText] = useState("");
        const [replySubmitting, setReplySubmitting] = useState(false);

        const onReply = async () => {
            if (!replyText.trim()) return;

            // Gate: require login to reply
            if (!requireAuth("Sign in to reply to discussions")) return;

            try {
                setReplySubmitting(true);
                await api.postDiscussion(questionId, replyText, comment.id);
                await fetchDiscussions();
                setIsReplying(false);
                setReplyText("");
            } catch (err) {
                alert("Failed to reply");
            } finally {
                setReplySubmitting(false);
            }
        };

        const handleReplyClick = () => {
            // Gate: require login to open reply box
            if (!requireAuth("Sign in to reply to discussions")) return;
            setIsReplying(!isReplying);
        };

        // Only show delete button if user owns this comment
        const canDelete = user && String(user.id) === String(comment.user_id);

        return (
            <div className={`flex flex-col gap-2 ${depth > 0 ? "ml-4 pl-4 border-l-2 border-slate-100 dark:border-white/5" : "bg-white dark:bg-card-dark p-4 rounded-xl border border-slate-100 dark:border-white/5"}`}>
                {/* Meta */}
                <div className="flex justify-between items-start">
                    <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-[10px] text-white font-bold">
                            U
                        </div>
                        <span className="text-xs font-bold text-slate-700 dark:text-slate-300">User {comment.user_id}</span>
                        <span className="text-[10px] text-slate-400 dark:text-gray-500">{new Date(comment.created_at).toLocaleDateString()}</span>
                    </div>
                </div>

                {/* Content */}
                <div className="text-sm text-slate-800 dark:text-slate-200 mt-1 mb-2">
                    <LatexRenderer text={comment.content} />
                </div>

                {/* Actions */}
                <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-gray-400">
                    <button
                        onClick={() => handleVote(comment.id, 'upvote')}
                        className="flex items-center gap-1 hover:text-green-500 transition-colors"
                    >
                        <ThumbsUp size={14} />
                        <span>{comment.upvotes}</span>
                    </button>
                    <button
                        onClick={() => handleVote(comment.id, 'downvote')}
                        className="flex items-center gap-1 hover:text-red-500 transition-colors"
                    >
                        <ThumbsDown size={14} />
                        <span>{comment.downvotes}</span>
                    </button>
                    <button
                        onClick={handleReplyClick}
                        className="flex items-center gap-1 hover:text-primary transition-colors"
                    >
                        <Reply size={14} />
                        Reply
                    </button>
                    {/* Only show delete for own comments */}
                    {canDelete && (
                        <button
                            onClick={() => handleDelete(comment.id)}
                            className="flex items-center gap-1 hover:text-red-500 ml-auto transition-colors"
                        >
                            <Trash2 size={14} />
                        </button>
                    )}
                </div>

                {/* Reply Input — only visible when user is logged in and replying */}
                {isReplying && (
                    <div className="mt-3 flex gap-2">
                        <textarea
                            value={replyText}
                            onChange={(e) => setReplyText(e.target.value)}
                            className="flex-1 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg p-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                            placeholder="Write a reply..."
                            rows={2}
                        />
                        <button
                            onClick={onReply}
                            disabled={replySubmitting}
                            className="bg-primary text-white p-2 rounded-lg h-fit hover:bg-blue-600 transition-colors disabled:opacity-50"
                        >
                            {replySubmitting ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                        </button>
                    </div>
                )}

                {/* Nested Replies */}
                {comment.children && comment.children.length > 0 && (
                    <div className="mt-2 flex flex-col gap-3">
                        {comment.children.map(child => (
                            <CommentItem key={child.id} comment={child} depth={depth + 1} />
                        ))}
                    </div>
                )}
            </div>
        );
    };

    if (loading) return (
        <div className="flex justify-center p-8">
            <Loader2 className="animate-spin text-slate-400" />
        </div>
    );

    if (error) return (
        <div className="text-center p-8 text-red-500 text-sm">
            {error}
        </div>
    );

    return (
        <div className="flex flex-col h-full bg-slate-50/50 dark:bg-black/20 rounded-2xl border border-slate-100 dark:border-white/5 overflow-hidden">
            <div className="p-4 border-b border-slate-100 dark:border-white/5 bg-white dark:bg-card-dark flex justify-between alignItems-center">
                <h3 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <MessageSquare size={18} className="text-primary" />
                    Discussion
                    <span className="bg-slate-100 dark:bg-white/10 text-slate-500 dark:text-slate-300 text-[10px] px-2 py-0.5 rounded-full">{discussions.length}</span>
                </h3>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {commentTree.length === 0 ? (
                    <div className="text-center py-10 text-slate-400 dark:text-gray-500 text-sm">
                        No discussions yet. Be the first to start a thread!
                    </div>
                ) : (
                    commentTree.map(comment => (
                        <CommentItem key={comment.id} comment={comment} />
                    ))
                )}
            </div>

            {/* Comment Input Area — different for guests vs logged-in users */}
            <div className="p-4 bg-white dark:bg-card-dark border-t border-slate-100 dark:border-white/5">
                {user ? (
                    /* Logged-in: show the real comment textarea */
                    <div className="relative">
                        <textarea
                            value={newComment}
                            onChange={(e) => setNewComment(e.target.value)}
                            className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl p-3 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all resize-none"
                            placeholder="Add to the discussion (Markdown/LaTeX supported)..."
                            rows={2}
                        />
                        <button
                            onClick={() => handlePost()}
                            disabled={submitting || !newComment.trim()}
                            className="absolute right-2 bottom-2 p-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-primary/20"
                        >
                            {submitting ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                        </button>
                    </div>
                ) : (
                    /* Guest: show a styled sign-in prompt */
                    <button
                        onClick={() => requireAuth("Create a free account to join the discussion")}
                        className="w-full flex items-center justify-center gap-3 py-4 px-4 bg-slate-50 dark:bg-white/5 border-2 border-dashed border-slate-200 dark:border-white/10 rounded-xl text-slate-500 dark:text-slate-400 hover:border-primary hover:text-primary dark:hover:border-primary dark:hover:text-primary transition-all cursor-pointer group"
                    >
                        <LogIn size={18} className="group-hover:scale-110 transition-transform" />
                        <span className="text-sm font-medium">Sign in to join the discussion</span>
                    </button>
                )}
                {user && (
                    <p className="text-[10px] text-slate-400 mt-2 ml-1">
                        Supports Markdown and LaTeX. Keep discussions respectful and relevant.
                    </p>
                )}
            </div>
        </div>
    );
};

export default DiscussionSection;
