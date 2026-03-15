
import React, { useState, useEffect } from 'react';
import {
    Menu, ChevronRight, Search, Sun, Moon, Bell, Signal,
    CheckCircle, Eye, Bookmark, Flag, ChevronLeft, Lightbulb, History
} from 'lucide-react';
import { api } from '../utils/api';
import LatexRenderer from './LatexRenderer';
import QuestionCard from './QuestionCard';
import { useAuth } from '../context/AuthContext';
import { TierViews } from './premium/TierViews';
import { cn } from './premium/ui';

const QuestionDetail = ({ questionId, onBack }) => {
    const [question, setQuestion] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedOption, setSelectedOption] = useState(null);
    const [showSolution, setShowSolution] = useState(false);
    const [isChecked, setIsChecked] = useState(false);
    const [guestAttempts, setGuestAttempts] = useState(() => {
        return parseInt(localStorage.getItem('guest_attempts') || '0');
    });
    const [showAuthModal, setShowAuthModal] = useState(false);
    const [hasUsedDailySolution, setHasUsedDailySolution] = useState(false);

    const startTimeRef = React.useRef(Date.now());
    const { user, isPremium } = useAuth();

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
                setHasUsedDailySolution(false);
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

            if (!user) {
                const newAttempts = guestAttempts + 1;
                setGuestAttempts(newAttempts);
                localStorage.setItem('guest_attempts', newAttempts.toString());
                
                if (newAttempts >= 4) {
                    setShowAuthModal(true);
                    return;
                }
            }

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

    const handleShowSolutionToggle = () => {
        if (showSolution) {
            setShowSolution(false);
            return;
        }

        if (isPremium || hasUsedDailySolution) {
            setShowSolution(true);
            return;
        }

        const today = new Date().toDateString();
        let lastReset = localStorage.getItem('last_reset_date');
        let count = parseInt(localStorage.getItem('solution_count') || '0');

        if (lastReset !== today) {
            count = 0;
            localStorage.setItem('last_reset_date', today);
        }

        if (count < 3) {
            count++;
            localStorage.setItem('solution_count', count.toString());
            setHasUsedDailySolution(true);
            setShowSolution(true);
        } else {
            // Out of free solutions, just show blurred view
            setShowSolution(true);
        }
    };

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
                                    onClick={() => {
                                        if (!user && guestAttempts >= 3) {
                                            setShowAuthModal(true);
                                        } else {
                                            handleCheckAnswer();
                                        }
                                    }}
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
                                onClick={handleShowSolutionToggle}
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
                        <div className={cn("relative z-10", !(isPremium || hasUsedDailySolution) && "blur-md select-none pointer-events-none")}>
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

                        {!(isPremium || hasUsedDailySolution) && (
                            <div className="absolute inset-0 z-20 flex items-center justify-center p-6 bg-gradient-to-b from-transparent via-white/40 to-white/80 dark:via-black/20 dark:to-[#0f1323]/80">
                                <div className="bg-white dark:bg-slate-900 p-8 rounded-3xl shadow-2xl border border-slate-200 dark:border-white/10 text-center max-w-sm animate-fade-in-up">
                                    <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                        <Sparkles className="text-primary" size={32} />
                                    </div>
                                    <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Unlock Pro Solutions</h4>
                                    <p className="text-slate-500 dark:text-gray-400 text-sm mb-6">
                                        Get step-by-step derivations and in-depth research insights for this question.
                                    </p>
                                    <button
                                        onClick={() => { /* Navigate to premium or emit event */ }}
                                        className="w-full bg-primary hover:bg-blue-600 text-white py-3 rounded-xl font-bold shadow-lg shadow-primary/20 transition-all transform hover:-translate-y-1 active:scale-95"
                                    >
                                        Upgrade to Pro
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Premium Analysis Tiers */}
                {/* 
                    Premium access requires:
                    1. User must be logged in
                    2. User must have premium subscription OR active free trial
                    
                    TODO: Add backend API to check subscription status
                    For now, we'll check if user is logged in as a basic gate
                */}
                <TierViews
                    question={question}
                    isPremium={isPremium}
                />
            </div>

            {/* Guest Limit Modal */}
            {showAuthModal && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
                    <div className="bg-white dark:bg-card-dark max-w-md w-full rounded-[2.5rem] shadow-2xl border border-slate-200 dark:border-white/5 overflow-hidden animate-fade-in-up">
                        <div className="p-10 text-center">
                            <div className="w-20 h-20 bg-primary/10 rounded-3xl flex items-center justify-center mx-auto mb-6 text-primary">
                                <History size={40} />
                            </div>
                            <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-3 tracking-tight">Free Daily Limit Reached</h3>
                            <p className="text-slate-500 dark:text-gray-400 mb-8 leading-relaxed font-medium">
                                Sign up for free to save your progress and continue practicing with unlimited attempts.
                            </p>
                            <div className="flex flex-col gap-3">
                                <button
                                    onClick={() => {
                                        setShowAuthModal(false);
                                        // Trigger login/signup modal from context
                                        window.dispatchEvent(new CustomEvent('open-auth-modal'));
                                    }}
                                    className="w-full bg-primary hover:bg-blue-600 text-white py-4 rounded-2xl font-black shadow-xl shadow-primary/20 transition-all transform hover:-translate-y-1 active:scale-95"
                                >
                                    Sign Up to Continue
                                </button>
                                <button
                                    onClick={() => setShowAuthModal(false)}
                                    className="w-full text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 text-sm font-bold transition-colors py-2"
                                >
                                    Wait for tomorrow
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default QuestionDetail;


