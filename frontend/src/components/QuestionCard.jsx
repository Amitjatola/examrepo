import React from 'react';
import { Bookmark, ArrowRight } from 'lucide-react';
import LatexRenderer from './LatexRenderer';

const QuestionCard = ({ qNo, difficulty, marks, text, tags, type, onClick, question }) => {
    // Adapter if 'question' object is passed instead of direct props (handling legacy usage in App.jsx)
    if (question && !text) {
        text = question.question_text_latex || question.question_text;
        tags = question.concepts || [];
        qNo = question.question_id || '00';
        difficulty = question.difficulty_level || 'Medium'; // Mapped from backend data if available
        marks = question.marks || 4;
    }

    // Helper for difficulty colors
    const getDiffColor = (d) => {
        switch (d) {
            case 'Easy': return 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 ring-green-600/20';
            case 'Medium': return 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-400 ring-yellow-600/20';
            case 'Hard': return 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 ring-red-600/10';
            default: return 'bg-gray-50 text-gray-700'; // Fallback
        }
    }

    return (
        <div
            onClick={onClick}
            className="bg-white dark:bg-card-dark rounded-xl p-5 shadow-sm border border-[#f0f2f4] dark:border-border-dark hover:shadow-md hover:border-primary/30 dark:hover:border-primary/30 transition-all group cursor-pointer flex flex-col h-full min-w-0"
        >
            <div className="flex justify-between items-start mb-3">
                <div className="flex gap-2 flex-wrap">
                    <span className="inline-flex items-center rounded-md bg-[#f0f2f4] dark:bg-background-dark/50 px-2 py-1 text-xs font-medium text-[#617589] dark:text-gray-400 ring-1 ring-inset ring-gray-500/10">Q. {qNo}</span>
                    <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${getDiffColor(difficulty)}`}>{difficulty}</span>
                    <span className="inline-flex items-center rounded-md bg-[#f0f2f4] dark:bg-background-dark/50 px-2 py-1 text-xs font-medium text-[#617589] dark:text-gray-400 ring-1 ring-inset ring-gray-500/10">{marks} Marks</span>
                </div>
                <button className="text-gray-400 hover:text-primary transition-colors">
                    <Bookmark size={20} />
                </button>
            </div>

            <div className="text-slate-900 dark:text-white font-medium leading-relaxed mb-4 flex-grow line-clamp-3">
                <LatexRenderer text={text} />
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-[#f0f2f4] dark:border-border-dark mt-auto">
                <div className="flex items-center gap-2 flex-wrap">
                    {tags && tags.map((tag, idx) => (
                        <React.Fragment key={tag}>
                            <span className="text-xs font-medium text-[#617589] dark:text-gray-500 uppercase tracking-wide">{tag}</span>
                            {idx < tags.length - 1 && <span className="text-gray-300 dark:text-gray-700">•</span>}
                        </React.Fragment>
                    ))}
                </div>
                <button className="flex items-center gap-2 text-sm font-bold text-primary hover:text-blue-600 dark:hover:text-blue-400 transition-colors whitespace-nowrap">
                    Solve Now
                    <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                </button>
            </div>
        </div>
    )
}

export default QuestionCard;
