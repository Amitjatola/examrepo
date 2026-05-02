import React, { useState } from 'react';
import { BookOpen, Video, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { Card, MathText } from './ui';
import { cn } from './ui';

export const ReferenceStrip = ({ tier1, isPremium, onUpgrade }) => {
    const [open, setOpen] = useState(true);
    const books = tier1?.textbook_references || [];
    const videos = tier1?.video_references || [];
    if (books.length === 0 && videos.length === 0) return null;

    return (
        <Card className="p-0 overflow-hidden border border-slate-200 dark:border-border-dark mb-4">
            <button
                type="button"
                onClick={() => setOpen((o) => !o)}
                className="w-full flex items-center justify-between px-4 py-3 bg-slate-50 dark:bg-white/5 hover:bg-slate-100 dark:hover:bg-white/10 transition-colors"
            >
                <span className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <BookOpen size={18} className="text-primary" />
                    References
                </span>
                {open ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>
            {open && (
                <div
                    className={cn(
                        'p-4 border-t border-slate-200 dark:border-border-dark relative',
                        !isPremium && 'blur-md select-none pointer-events-none min-h-[100px]'
                    )}
                >
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {books.length > 0 && (
                            <div>
                                <h4 className="text-xs font-bold uppercase text-slate-500 mb-2">Textbooks</h4>
                                <ul className="space-y-3">
                                    {books.map((b, i) => (
                                        <li
                                            key={i}
                                            className="rounded-lg border border-slate-100 dark:border-white/10 p-3 text-sm"
                                        >
                                            <p className="font-semibold text-slate-900 dark:text-white">
                                                {b.book || 'Book'}
                                            </p>
                                            {b.author && (
                                                <p className="text-xs text-slate-500 mt-0.5">by {b.author}</p>
                                            )}
                                            <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                                                {b.chapter_title && `Ch. ${b.chapter_number || ''} ${b.chapter_title}`.trim()}
                                                {b.page_range && ` · pp. ${b.page_range}`}
                                                {b.relevance_score != null &&
                                                    ` · ${Math.round(Number(b.relevance_score) * 100)}% relevance`}
                                            </p>
                                            {b.text_snippet && (
                                                <blockquote className="mt-2 text-xs italic text-slate-500 border-l-2 border-primary/40 pl-2">
                                                    <MathText>{b.text_snippet}</MathText>
                                                </blockquote>
                                            )}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                        {videos.length > 0 && (
                            <div>
                                <h4 className="text-xs font-bold uppercase text-slate-500 mb-2 flex items-center gap-1">
                                    <Video size={14} /> Videos
                                </h4>
                                <ul className="space-y-3">
                                    {videos.map((v, i) => (
                                        <li
                                            key={i}
                                            className="rounded-lg border border-slate-100 dark:border-white/10 p-3 text-sm"
                                        >
                                            <p className="font-semibold text-slate-900 dark:text-white">
                                                {v.topic_covered || 'Lecture'}
                                            </p>
                                            {v.professor && (
                                                <p className="text-xs text-slate-500 mt-0.5">{v.professor}</p>
                                            )}
                                            {v.video_url && (
                                                <a
                                                    href={v.video_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="inline-flex items-center gap-1 text-primary text-xs font-semibold mt-2 hover:underline"
                                                >
                                                    Open <ExternalLink size={12} />
                                                </a>
                                            )}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                </div>
            )}
            {!isPremium && open && (
                <div className="px-4 pb-4 -mt-2 flex justify-center">
                    <button
                        type="button"
                        onClick={onUpgrade}
                        className="text-sm font-semibold text-primary hover:underline"
                    >
                        Unlock references with Pro
                    </button>
                </div>
            )}
        </Card>
    );
};
