
import React, { useState, useEffect } from 'react';
import {
    Menu, ChevronRight, Search, Sun, Moon, Bell, Signal,
    CheckCircle, Eye, Bookmark, Flag, ChevronLeft, Lightbulb
} from 'lucide-react';
import { api } from '../utils/api';
import LatexRenderer from './LatexRenderer';
import QuestionCard from './QuestionCard'; // Reusing the unified card for parts of the UI if needed, or just standardizing styles
import { useAuth } from '../context/AuthContext';

const QuestionDetail = ({ questionId, onBack }) => {
    const [question, setQuestion] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedOption, setSelectedOption] = useState(null);
    const [showSolution, setShowSolution] = useState(false);
    const [isChecked, setIsChecked] = useState(false);

    const startTimeRef = React.useRef(Date.now());
    const { user } = useAuth();

    useEffect(() => {
        const fetchQuestion = async () => {
            if (!questionId) return;
            setLoading(true);
            try {
                // Fetch basic detail
                const data = await api.get(`/questions/${questionId}`);
                setQuestion(data);
                // Reset state when loading new question
                setSelectedOption(null);
                setShowSolution(false);
                setIsChecked(false);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchQuestion();
    }, [questionId]);

    // Reset timer when question changes
    useEffect(() => {
        startTimeRef.current = Date.now();
    }, [questionId]);

    if (loading) return <div className="p-8 flex justify-center text-gray-500">Loading question...</div>;
    if (error) return <div className="p-8 flex justify-center text-red-500">Error: {error}</div>;
    if (!question) return <div className="p-8 flex justify-center text-gray-500">Question not found.</div>;

    // Helper for difficulty colors
    const getDiffColor = (d) => {
        // Default to Medium if undefined
        const diff = d ? d.toLowerCase() : 'medium';
        if (diff === 'easy') return { bg: 'bg-green-50 dark:bg-green-900/20', border: 'border-green-100 dark:border-green-900/30', text: 'text-green-700 dark:text-green-300', icon: 'text-green-600 dark:text-green-400' };
        if (diff === 'hard') return { bg: 'bg-red-50 dark:bg-red-900/20', border: 'border-red-100 dark:border-red-900/30', text: 'text-red-700 dark:text-red-300', icon: 'text-red-600 dark:text-red-400' };
        return { bg: 'bg-yellow-50 dark:bg-yellow-900/20', border: 'border-yellow-100 dark:border-yellow-900/30', text: 'text-yellow-700 dark:text-yellow-300', icon: 'text-yellow-600 dark:text-yellow-400' };
    };

    const diffStyles = getDiffColor(question.difficulty_level || 'Medium'); // Using mapped difficulty if available, else standard

    // Extract detailed solution data
    const tier1 = question.tier_1_core_research || {};
    // Steps are in tier_1_core_research.explanation.step_by_step
    // Note: If accessing through explanation property directly (depends on schema flattening), checks both.
    const explanation = tier1.explanation || question.explanation || {};
    const steps = (explanation.step_by_step || []).filter(s => s && s.trim() !== "");
    // Reasoning is in tier_1_core_research.answer_validation.reasoning
    const validation = tier1.answer_validation || {};
    const reasoning = validation.reasoning || "";

    const handleCheckAnswer = async () => {
        if (!selectedOption) return;
        setIsChecked(true);

        // Record attempt if user is logged in
        // Ideally we should use the user object from context, but let's assume api handles auth header
        try {
            const timeTaken = Math.round((Date.now() - startTimeRef.current) / 1000);
            const isCorrect = selectedOption === question.answer_key;

            // Fire and forget, or handle error? For UX speed, fire and forget or simple log
            await api.post(`/questions/${question.question_id}/attempt`, {
                is_correct: isCorrect,
                time_taken_seconds: timeTaken
            });
        } catch (err) {
            console.error("Failed to record attempt:", err);
        }
    };

    const isCorrect = selectedOption === question.answer_key;

    return (
        <div className="flex-1 overflow-y-auto p-4 md:p-8 flex justify-center bg-background-light dark:bg-background-dark h-full">
            <div className="max-w-4xl w-full flex flex-col gap-6 pb-20">
                {/* Question Card */}
                <div className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-[#e5e7eb] dark:border-border-dark overflow-hidden">
                    {/* Card Header / Meta */}
                    <div className="px-6 md:px-8 py-5 border-b border-[#f0f2f4] dark:border-border-dark flex flex-wrap justify-between items-center gap-4">
                        <div>
                            <h2 className="text-slate-900 dark:text-white text-2xl font-bold leading-tight font-display">{question.question_id}</h2>
                            <p className="text-slate-500 dark:text-gray-400 text-sm mt-1">{question.question_type} • {question.marks} Marks</p>
                        </div>
                        <div className="flex gap-2 flex-wrap">
                            <div className={`flex h-7 items-center justify-center gap-x-1.5 rounded-full px-3 border ${diffStyles.bg} ${diffStyles.border}`}>
                                <Signal size={16} className={diffStyles.icon} />
                                <p className={`${diffStyles.text} text-xs font-semibold uppercase tracking-wide`}>{question.difficulty_level || 'Medium'}</p>
                            </div>
                            <div className="flex h-7 items-center justify-center gap-x-1.5 rounded-full bg-[#f0f2f4] dark:bg-landing-bg-dark/50 px-3">
                                <p className="text-slate-900 dark:text-gray-200 text-xs font-semibold uppercase tracking-wide">Year {question.year}</p>
                            </div>
                            {question.source && (
                                <div className="flex h-7 items-center justify-center gap-x-1.5 rounded-full bg-blue-50 dark:bg-blue-900/20 px-3 border border-blue-100 dark:border-blue-900/30">
                                    <p className="text-blue-700 dark:text-blue-300 text-xs font-semibold uppercase tracking-wide">{question.source}</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Question Body */}
                    <div className="px-6 md:px-8 py-6">
                        <div className="text-slate-900 dark:text-gray-200 text-lg leading-relaxed font-normal">
                            <LatexRenderer text={question.question_text_latex || question.question_text} />
                        </div>
                    </div>

                    {/* Answer Options */}
                    {question.options && (
                        <div className="px-6 md:px-8 pb-8 flex flex-col gap-3">
                            {Object.entries(question.options).map(([key, value]) => {
                                let optionStyleClass = `group relative flex cursor-pointer rounded-lg border p-4 transition-all `;
                                let indicatorClass = "";

                                if (isChecked) {
                                    if (key === question.answer_key) {
                                        // Correct Answer -> Green
                                        optionStyleClass += 'border-green-500 bg-green-50 dark:bg-green-900/20 shadow-md';
                                        indicatorClass = 'border-green-500 bg-green-500 text-white';
                                    } else if (selectedOption === key) {
                                        // Wrong Selection -> Red
                                        optionStyleClass += 'border-red-500 bg-red-50 dark:bg-red-900/20 shadow-md';
                                        indicatorClass = 'border-red-500 bg-red-500 text-white';
                                    } else {
                                        // Others -> Dimmed
                                        optionStyleClass += 'border-[#e5e7eb] dark:border-border-dark bg-white dark:bg-card-dark opacity-60';
                                        indicatorClass = 'border-[#cbd5e1] text-[#64748b]';
                                    }
                                } else {
                                    // Normal State
                                    if (selectedOption === key) {
                                        optionStyleClass += 'border-primary bg-blue-50/50 dark:bg-blue-900/10 shadow-md';
                                        indicatorClass = 'border-primary bg-primary text-white';
                                    } else {
                                        optionStyleClass += 'border-[#e5e7eb] dark:border-border-dark bg-white dark:bg-card-dark hover:bg-[#f9fafb] dark:hover:bg-landing-border/20';
                                        indicatorClass = 'border-[#cbd5e1] text-[#64748b]';
                                    }
                                }

                                return (
                                    <label
                                        key={key}
                                        className={optionStyleClass}
                                    >
                                        <input
                                            type="radio"
                                            name="answer"
                                            className="peer sr-only"
                                            checked={selectedOption === key}
                                            onChange={() => !isChecked && setSelectedOption(key)}
                                            disabled={isChecked}
                                        />
                                        <div className="flex w-full items-center gap-4">
                                            <div className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 text-xs font-bold transition-colors ${indicatorClass}`}>
                                                {key}
                                            </div>
                                            <div className="text-slate-900 dark:text-gray-200 text-base font-medium">
                                                <LatexRenderer text={value} />
                                            </div>
                                        </div>

                                        {/* Feedback Icons */}
                                        {isChecked && key === question.answer_key && (
                                            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-green-600">
                                                <CheckCircle size={24} />
                                            </div>
                                        )}
                                        {isChecked && selectedOption === key && key !== question.answer_key && (
                                            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-red-500 font-bold text-xl">
                                                ✕
                                            </div>
                                        )}
                                        {!isChecked && selectedOption === key && (
                                            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-primary">
                                                <CheckCircle size={24} />
                                            </div>
                                        )}
                                    </label>
                                );
                            })}
                        </div>
                    )}

                    {/* Actions Toolbar */}
                    <div className="px-6 md:px-8 py-4 bg-gray-50 dark:bg-landing-bg-dark/30 border-t border-[#e5e7eb] dark:border-border-dark flex flex-wrap justify-between items-center gap-4">
                        <div className="flex gap-3">
                            {!isChecked ? (
                                <button
                                    onClick={handleCheckAnswer}
                                    disabled={!selectedOption}
                                    className={`px-5 py-2.5 rounded-lg text-sm font-semibold shadow-sm transition-all flex items-center gap-2 
                                        ${!selectedOption
                                            ? 'bg-gray-300 dark:bg-gray-700 text-gray-500 cursor-not-allowed'
                                            : 'bg-primary hover:bg-blue-600 text-white cursor-pointer'}`}
                                >
                                    <CheckCircle size={18} />
                                    Check Answer
                                </button>
                            ) : (
                                <div className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold border ${isCorrect ? 'text-green-700 bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800' : 'text-red-700 bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800'}`}>
                                    {isCorrect ? <CheckCircle size={18} /> : <span className="font-bold">✕</span>}
                                    {isCorrect ? 'Correct Answer' : 'Incorrect Answer'}
                                </div>
                            )}

                            <button
                                onClick={() => setShowSolution(!showSolution)}
                                className="bg-white dark:bg-card-dark border border-[#e5e7eb] dark:border-border-dark hover:bg-gray-50 dark:hover:bg-white/5 text-slate-900 dark:text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2 cursor-pointer"
                            >
                                <Eye size={18} />
                                {showSolution ? 'Hide Solution' : 'Show Solution'}
                            </button>
                        </div>
                        <div className="flex items-center gap-2">
                            <button className="bg-white dark:bg-card-dark border border-[#e5e7eb] dark:border-border-dark hover:bg-gray-50 dark:hover:bg-white/5 text-slate-900 dark:text-white px-3 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2 cursor-pointer">
                                <Bookmark size={18} />
                                <span className="hidden sm:inline">Map</span>
                            </button>
                            <button className="p-2 text-slate-500 hover:bg-gray-200 dark:hover:bg-white/10 rounded-lg transition-colors cursor-pointer" title="Report Error">
                                <Flag size={20} />
                            </button>
                            <div className="h-6 w-px bg-gray-300 dark:bg-gray-600 mx-1"></div>
                            <button
                                onClick={onBack}
                                className="flex items-center gap-1 text-slate-500 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-white/10 transition-colors cursor-pointer"
                            >
                                <ChevronLeft size={20} />
                                <span className="text-sm font-medium hidden sm:inline">Back</span>
                            </button>
                        </div>
                    </div>
                </div>

                {/* Collapsible Solution Panel */}
                {showSolution && (
                    <div className="bg-blue-50/50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-900/20 rounded-xl p-6 md:p-8 animate-fade-in relative overflow-hidden">
                        <div className="relative z-10">
                            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                                <CheckCircle className="text-primary" size={24} />
                                Correct Answer: {question.answer_key}
                            </h3>
                            <div className="prose prose-blue dark:prose-invert max-w-none text-slate-900 dark:text-gray-200 space-y-6">
                                {/* Reasoning Text */}
                                {reasoning && (
                                    <div>
                                        <h4 className="font-semibold text-sm text-blue-800 dark:text-blue-300 uppercase tracking-wide mb-2">Detailed Reasoning</h4>
                                        <div className="text-base leading-relaxed text-gray-800 dark:text-gray-200">
                                            <LatexRenderer text={reasoning} />
                                        </div>
                                    </div>
                                )}

                                {/* Steps */}
                                {steps.length > 0 && (
                                    <div>
                                        <h4 className="font-semibold text-sm text-blue-800 dark:text-blue-300 uppercase tracking-wide mb-2">Step-by-Step Validation</h4>
                                        <ul className="list-disc pl-5 space-y-3">
                                            {steps.map((step, idx) => (
                                                <li key={idx} className="text-gray-800 dark:text-gray-200">
                                                    <LatexRenderer text={step} />
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {!reasoning && steps.length === 0 && (
                                    <p className="italic text-gray-500">Detailed explanation coming soon.</p>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default QuestionDetail;


