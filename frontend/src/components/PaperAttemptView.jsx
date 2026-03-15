
import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import QuestionCard from './QuestionCard'; // We might reuse or adapt this, but the design is specific here
import { ChevronLeft, ChevronRight, CheckCircle, XCircle, Clock, AlertCircle, Sparkles, Flag, Bookmark, MessageSquare, Lightbulb } from 'lucide-react';
import LatexRenderer from './LatexRenderer';
import DiscussionSection from './DiscussionSection';

// A specialized Question View for the Year-based attempt flow
const PaperAttemptView = ({ year, onBack, onPremium, user, isPremium }) => {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [showSolution, setShowSolution] = useState(false);
    const [selectedOption, setSelectedOption] = useState(null);
    const [isCorrect, setIsCorrect] = useState(null);
    const [seconds, setSeconds] = useState(0);
    const [isStarted, setIsStarted] = useState(false);
    const [showDiscuss, setShowDiscuss] = useState(false);
    const [guestAttempts, setGuestAttempts] = useState(() => {
        return parseInt(localStorage.getItem('guest_attempts') || '0');
    });
    const [showSignUpToast, setShowSignUpToast] = useState(false);
    const [hasUsedDailySolution, setHasUsedDailySolution] = useState(false);
    const { cn } = { cn: (...classes) => classes.filter(Boolean).join(' ') }; // Fallback helper or use proper utility

    // Session Timer logic - only runs if started
    useEffect(() => {
        if (!isStarted) return;

        const interval = setInterval(() => {
            setSeconds(prev => prev + 1);
        }, 1000);
        return () => clearInterval(interval);
    }, [isStarted]);

    const formatTime = (totalSeconds) => {
        const h = Math.floor(totalSeconds / 3600);
        const m = Math.floor((totalSeconds % 3600) / 60);
        const s = totalSeconds % 60;
        return [h, m, s].map(v => v < 10 ? "0" + v : v).join(":");
    };

    // Fetch questions for the year
    useEffect(() => {
        const fetchQuestions = async () => {
            setLoading(true);
            try {
                // Fetch full paper (page_size 100 fixed previously ensures full year)
                const data = await api.get('/questions', { year: year, page_size: 100 });
                // Sort by question_number to ensure Q1 -> Q65 order
                const sorted = data.sort((a, b) => (a.question_number || 0) - (b.question_number || 0));
                setQuestions(sorted);
            } catch (err) {
                console.error("Failed to fetch paper:", err);
            } finally {
                setLoading(false);
            }
        };

        if (year) fetchQuestions();
    }, [year]);

    const startTimeRef = React.useRef(Date.now());

    // Reset state on question change
    useEffect(() => {
        startTimeRef.current = Date.now();
        setShowSolution(false);
        setSelectedOption(null);
        setIsCorrect(null);
        setHasUsedDailySolution(false);
    }, [currentIndex]);

    const currentQuestion = questions[currentIndex];
    const totalQuestions = questions.length;
    const progress = totalQuestions > 0 ? Math.round(((currentIndex + 1) / totalQuestions) * 100) : 0;

    console.log('[DEBUG] PaperAttemptView State:', {
        isStarted,
        totalQuestions,
        currentIndex,
        currentQuestion,
        questionsSample: questions.slice(0, 1)
    });

    const handleNext = () => {
        if (currentIndex < totalQuestions - 1) {
            setCurrentIndex(prev => prev + 1);
        }
    };

    const handlePrev = () => {
        if (currentIndex > 0) {
            setCurrentIndex(prev => prev - 1);
        }
    };

    const handleCheck = async () => {
        if (!selectedOption || !currentQuestion) return;

        // Robust comparison: normalize keys
        const correctKey = (currentQuestion.answer_key || '').trim().toUpperCase();
        const selectedKey = (selectedOption || '').trim().toUpperCase();

        const isRight = selectedKey === correctKey;
        setIsCorrect(isRight);

        if (!user) {
            const newAttempts = guestAttempts + 1;
            setGuestAttempts(newAttempts);
            localStorage.setItem('guest_attempts', newAttempts.toString());
            
            // Show a nudge toast after 5 guest questions
            if (newAttempts >= 5) {
                setShowSignUpToast(true);
                setTimeout(() => setShowSignUpToast(false), 6000);
            }
            // Don't save to DB for guests
            return;
        }

        // Record Attempt (only for logged-in users)
        try {
            const timeTaken = Math.round((Date.now() - startTimeRef.current) / 1000);
            await api.post(`/questions/${currentQuestion.question_id}/attempt`, {
                is_correct: isRight,
                time_taken_seconds: timeTaken
            });
        } catch (err) {
            console.error("Failed to record attempt:", err);
        }
    };

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

    if (loading && !isStarted) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center bg-background-light dark:bg-background-dark h-full">
                <div className="flex flex-col items-center gap-6">
                    <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin shadow-lg shadow-primary/20"></div>
                    <div className="flex flex-col items-center gap-2">
                        <p className="text-xl font-bold text-slate-900 dark:text-white animate-pulse tracking-tight">Initializing Session</p>
                        <p className="text-sm text-slate-500 dark:text-gray-400 font-medium tracking-wide font-mono">Preparing GATE {year} Material...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (!isStarted) {
        return (
            <div className="flex-1 flex flex-col h-full bg-slate-50 dark:bg-[#0f1323] font-display relative overflow-hidden">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(56,88,250,0.08),transparent_50%)]"></div>

                {/* Header-like Nav for Back */}
                <div className="px-8 py-6 relative z-10">
                    <button
                        onClick={onBack}
                        className="flex items-center text-slate-500 hover:text-primary transition-all group"
                    >
                        <div className="bg-white dark:bg-white/5 p-2 rounded-xl mr-3 shadow-sm group-hover:bg-primary/10 group-hover:text-primary transition-all border border-slate-200/50 dark:border-white/5">
                            <ChevronLeft size={20} />
                        </div>
                        <span className="font-semibold tracking-tight">Back to Library</span>
                    </button>
                </div>

                <div className="flex-1 flex items-center justify-center p-4 relative z-10 overflow-y-auto">
                    <div className="w-full max-w-sm bg-white dark:bg-card-dark rounded-[2rem] shadow-2xl border border-slate-200/60 dark:border-white/5 overflow-hidden animate-fade-in-up">
                        <div className="p-6 text-center">
                            <div className="w-12 h-12 bg-gradient-to-br from-primary/20 to-blue-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-inner group transition-transform duration-500 hover:rotate-12">
                                <Clock size={24} className="text-primary group-hover:animate-pulse" />
                            </div>

                            <h1 className="text-2xl md:text-3xl font-black text-slate-900 dark:text-white mb-2 tracking-tighter leading-tight">
                                <span className="text-primary">GATE</span> Aerospace <span className="opacity-40">{year}</span>
                            </h1>
                            <p className="text-slate-500 dark:text-gray-400 text-xs mb-5 max-w-xs mx-auto leading-relaxed font-medium">
                                Ready to challenge yourself? This official exam contains <span className="text-slate-900 dark:text-white font-bold">65 questions</span> to be completed in <span className="text-slate-900 dark:text-white font-bold">180 minutes</span>.
                            </p>

                            <div className="grid grid-cols-2 gap-3 mb-5 text-left">
                                <div className="bg-slate-50 dark:bg-white/5 p-3 rounded-xl border border-slate-100 dark:border-white/5 group hover:border-primary/30 hover:bg-white/10 transition-all duration-300 relative overflow-hidden">
                                    <div className="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-20 transition-opacity text-primary">
                                        <CheckCircle size={24} />
                                    </div>
                                    <div className="text-xl font-black text-slate-900 dark:text-white mb-0.5 leading-none relative z-10">65</div>
                                    <div className="text-[8px] uppercase tracking-[0.2em] text-slate-400 font-black relative z-10">Questions</div>
                                </div>
                                <div className="bg-slate-50 dark:bg-white/5 p-3 rounded-xl border border-slate-100 dark:border-white/5 group hover:border-primary/30 hover:bg-white/10 transition-all duration-300 relative overflow-hidden">
                                    <div className="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-20 transition-opacity text-primary">
                                        <Clock size={24} />
                                    </div>
                                    <div className="text-xl font-black text-slate-900 dark:text-white mb-0.5 leading-none relative z-10">180</div>
                                    <div className="text-[8px] uppercase tracking-[0.2em] text-slate-400 font-black relative z-10">Minutes</div>
                                </div>
                            </div>

                            <button
                                onClick={() => setIsStarted(true)}
                                className="w-full bg-gradient-to-r from-primary to-blue-600 hover:to-blue-500 text-white py-3 rounded-xl font-black text-base shadow-xl shadow-primary/30 transition-all transform hover:-translate-y-1 active:scale-95 flex items-center justify-center gap-2 group relative overflow-hidden"
                            >
                                <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 blur-xl"></div>
                                <span className="relative z-10 flex items-center gap-2">Solve Now <ChevronRight size={18} className="transition-transform group-hover:translate-x-1" /></span>
                            </button>

                            <button
                                onClick={onPremium}
                                className="w-full mt-3 bg-slate-900 dark:bg-white text-white dark:text-slate-900 py-3 rounded-xl font-bold text-sm shadow-lg flex items-center justify-center gap-2 transition-transform active:scale-95 group border border-transparent hover:border-primary/50">
                                <Sparkles size={16} className="text-yellow-400 dark:text-yellow-500 animate-pulse" />
                                <span>Get Premium Solution</span>
                            </button>

                            <div className="mt-6 text-slate-400 dark:text-slate-500 text-[10px] font-bold uppercase tracking-widest flex items-center justify-center gap-2">
                                <div className="w-1 h-1 rounded-full bg-primary/50"></div>
                                <span className="opacity-70">The timer begins on click</span>
                                <div className="w-1 h-1 rounded-full bg-primary/50"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (!currentQuestion) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center bg-background-light dark:bg-background-dark h-full p-6 text-center">
                <div className="bg-red-50 dark:bg-red-900/10 p-4 rounded-2xl mb-6">
                    <XCircle size={48} className="text-red-500" />
                </div>
                <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-2">No Questions Loaded</h3>
                <p className="text-slate-500 dark:text-gray-400 max-w-xs mb-8">We couldn't find any questions for the year {year} in our database.</p>
                <button
                    onClick={onBack}
                    className="flex items-center gap-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-8 py-3 rounded-2xl font-bold shadow-lg transition-transform hover:scale-105 active:scale-95"
                >
                    <ChevronLeft size={20} />
                    Return to Library
                </button>
            </div>
        );
    }

    // Extract detailed explanation data similar to QuestionDetail
    const tier1 = currentQuestion.tier_1_core_research || {};
    // Steps are in tier_1_core_research.explanation.step_by_step
    const explanationData = tier1.explanation || currentQuestion.explanation || {};
    const steps = (explanationData.step_by_step || []).filter(s => s && s.trim() !== "");
    const validation = tier1.answer_validation || {};
    const reasoning = validation.reasoning || "";

    // Helper for difficulty colors (Consolidated from QuestionDetail)
    const getDiffColor = (d) => {
        const diff = d ? d.toLowerCase() : 'medium';
        if (diff === 'easy') return { bg: 'bg-green-50 dark:bg-green-900/20', border: 'border-green-100 dark:border-green-900/30', text: 'text-green-700 dark:text-green-300', icon: 'text-green-600 dark:text-green-400' };
        if (diff === 'hard') return { bg: 'bg-red-50 dark:bg-red-900/20', border: 'border-red-100 dark:border-red-900/30', text: 'text-red-700 dark:text-red-300', icon: 'text-red-600 dark:text-red-400' };
        return { bg: 'bg-yellow-50 dark:bg-yellow-900/20', border: 'border-yellow-100 dark:border-yellow-900/30', text: 'text-yellow-700 dark:text-yellow-300', icon: 'text-yellow-600 dark:text-yellow-400' };
    };
    const diffStyles = getDiffColor(currentQuestion.difficulty_level);

    return (
        <div className="flex-1 flex flex-col h-full bg-background-light dark:bg-background-dark font-display relative overflow-hidden">
            {/* Sticky Header with Navigation & Progress */}
            <div className="sticky top-0 z-20 bg-white/80 dark:bg-[#0f1323]/80 backdrop-blur-xl border-b border-slate-200/60 dark:border-white/5 px-4 py-2.5 flex items-center justify-between transition-all">
                <nav className="flex items-center text-sm font-medium">
                    <button
                        onClick={onBack}
                        className="flex items-center text-slate-500 hover:text-primary transition-all group"
                    >
                        <span className="bg-slate-100 dark:bg-white/5 p-1.5 rounded-lg mr-2 group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                            <ChevronLeft size={16} />
                        </span>
                        Paper {year}
                    </button>
                    <ChevronRight size={14} className="mx-3 text-slate-300 dark:text-white/10" />
                    <span className="text-slate-900 dark:text-white font-semibold">Question {currentQuestion.question_number}</span>
                </nav>
                <div className="flex items-center gap-5">
                    <div className="flex flex-col items-end mr-2 hidden sm:flex">
                        <div className="text-[10px] uppercase tracking-widest text-slate-400 dark:text-slate-500 font-bold mb-1.5">
                            Progress • {currentIndex + 1}/{totalQuestions}
                        </div>
                        <div className="w-32 h-1.5 bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-primary to-blue-400 rounded-full transition-all duration-500 ease-out shadow-[0_0_8px_rgba(56,88,250,0.4)]"
                                style={{ width: `${progress}%` }}
                            ></div>
                        </div>
                    </div>
                    <div className="h-8 w-[1px] bg-slate-200 dark:bg-white/5 mx-1 hidden sm:block"></div>
                    <div className="flex items-center gap-3 px-3 py-1.5 bg-slate-100 dark:bg-white/5 rounded-xl border border-slate-200/50 dark:border-white/5 shadow-inner">
                        <Clock size={16} className="text-primary animate-pulse" />
                        <span className="font-mono text-xs font-bold text-slate-700 dark:text-slate-300 tabular-nums">
                            {formatTime(seconds)}
                        </span>
                    </div>
                    <div className="h-8 w-[1px] bg-slate-200 dark:bg-white/5 mx-1 hidden sm:block"></div>
                    <div className="flex items-center gap-1.5">
                        <button className="p-2.5 text-slate-400 hover:text-primary hover:bg-primary/10 transition-all rounded-xl">
                            <Flag size={18} />
                        </button>
                        <button className="p-2.5 text-slate-400 hover:text-primary hover:bg-primary/10 transition-all rounded-xl">
                            <Bookmark size={18} />
                        </button>
                    </div>
                </div>
            </div>

            {/* Scrollable Content Container */}
            <div className="flex-1 overflow-y-auto scroll-smooth">
                <div className="w-full max-w-4xl mx-auto px-4 sm:px-6 py-4 flex flex-col pb-10">

                    {/* Question Card (Reflecting QuestionDetail Style) */}
                    <div className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-[#e5e7eb] dark:border-border-dark overflow-hidden mb-6">

                        {/* Card Header / Meta */}
                        <div className="px-5 py-3 border-b border-slate-100 dark:border-white/5 flex flex-wrap justify-between items-center gap-3 bg-gradient-to-r from-slate-50/50 to-white dark:from-white/5 dark:to-transparent">
                            <div>
                                <h2 className="text-slate-900 dark:text-white text-lg font-extrabold leading-tight tracking-tight mb-1 flex items-center gap-2">
                                    <span className="text-primary">#</span> Question {currentQuestion.question_number}
                                </h2>
                                <div className="flex items-center gap-2">
                                    <span className="bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded">
                                        {currentQuestion.subject || "General"}
                                    </span>
                                    <span className="text-slate-400 text-xs font-medium">•</span>
                                    <span className="text-slate-500 dark:text-gray-400 text-xs font-medium">
                                        {currentQuestion.marks} Mark{currentQuestion.marks !== 1 ? 's' : ''}
                                    </span>
                                </div>
                            </div>
                            <div className="flex gap-2 flex-wrap items-center">
                                {/* Difficulty Badge */}
                                <div className={`flex h-7 items-center justify-center gap-x-1.5 rounded-full px-3 border shadow-sm ${diffStyles.bg} ${diffStyles.border}`}>
                                    <div className={`w-1.5 h-1.5 rounded-full ${diffStyles.text} bg-current`}></div>
                                    <span className={`${diffStyles.text} text-[10px] font-bold uppercase tracking-wider`}>{currentQuestion.difficulty_level || 'Medium'}</span>
                                </div>
                                <div className="flex items-center bg-white dark:bg-slate-800/50 rounded-full border border-slate-200 dark:border-white/10 shadow-sm overflow-hidden p-1">
                                    <button
                                        onClick={handlePrev}
                                        disabled={currentIndex === 0}
                                        className="p-1.5 hover:bg-slate-100 dark:hover:bg-white/10 text-slate-500 dark:text-gray-400 disabled:opacity-20 disabled:cursor-not-allowed transition-all rounded-full"
                                        title="Previous Question"
                                    >
                                        <ChevronLeft size={18} />
                                    </button>
                                    <div className="w-[1px] h-4 bg-slate-200 dark:bg-white/10 mx-0.5"></div>
                                    <button
                                        onClick={handleNext}
                                        disabled={currentIndex === totalQuestions - 1}
                                        className="p-1.5 hover:bg-slate-100 dark:hover:bg-white/10 text-slate-500 dark:text-gray-400 disabled:opacity-20 disabled:cursor-not-allowed transition-all rounded-full"
                                        title="Next Question"
                                    >
                                        <ChevronRight size={18} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Question Body */}
                    <div className="px-5 py-5">
                        <div className="text-slate-900 dark:text-gray-100 text-base leading-relaxed font-medium prose dark:prose-invert max-w-none">
                            <LatexRenderer text={currentQuestion.question_text} />
                            {currentQuestion.question_text_latex && (
                                <div className="mt-4 p-4 bg-slate-50/50 dark:bg-white/5 rounded-xl border border-slate-100 dark:border-white/5 flex justify-center items-center overflow-x-auto shadow-inner">
                                    <div className="text-primary dark:text-blue-400">
                                        <LatexRenderer text={`$$${currentQuestion.question_text_latex}$$`} block={true} />
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Options */}
                    {currentQuestion.options && (
                        <div className="px-5 pb-5 flex flex-col gap-2">
                            {Object.entries(currentQuestion.options).map(([key, value]) => {
                                if (key === 'id') return null;

                                const isSelected = selectedOption === key;
                                // Robust comparison
                                const normalizedKey = key.trim().toUpperCase();
                                const normalizedCorrectKey = (currentQuestion.answer_key || '').trim().toUpperCase();
                                const isRightAnswer = normalizedKey === normalizedCorrectKey;

                                // Use explicit isCorrect=true/false from state, or null if not checked
                                const isUserWrong = isCorrect === false && isSelected;
                                const isUserRight = isCorrect === true && isSelected;

                                // Logic for styling:
                                // If checked:
                                // - Correct answer key gets Green
                                // - Wrong selected key gets Red
                                // - Others get Dimmed

                                let optionStyleClass = `group relative flex cursor-pointer rounded-xl border-2 p-3.5 transition-all duration-300 `;
                                let indicatorClass = "w-7 h-7 rounded-lg border-2 flex items-center justify-center font-bold text-sm transition-all duration-300 shadow-sm ";

                                if (isCorrect !== null) {
                                    // CHECKED STATE
                                    if (isRightAnswer) {
                                        // Always highlight correct answer in green if checked
                                        optionStyleClass += 'border-green-500 bg-green-50/50 dark:bg-green-500/10 shadow-[0_0_20px_rgba(34,197,94,0.15)] ring-1 ring-green-500/20';
                                        indicatorClass += 'border-green-500 bg-green-500 text-white';
                                    } else if (isSelected) {
                                        // Selected but Wrong -> Red
                                        optionStyleClass += 'border-red-500 bg-red-50/50 dark:bg-red-500/10 shadow-[0_0_20px_rgba(239,68,68,0.15)] ring-1 ring-red-500/20';
                                        indicatorClass += 'border-red-500 bg-red-500 text-white';
                                    } else {
                                        // Others -> Dimmed
                                        optionStyleClass += 'border-slate-100 dark:border-white/5 bg-white dark:bg-white/[0.02] opacity-40 grayscale-[0.5]';
                                        indicatorClass += 'border-slate-200 dark:border-white/10 text-slate-400';
                                    }
                                } else {
                                    // NORMAL STATE
                                    if (isSelected) {
                                        optionStyleClass += 'border-primary bg-blue-50/30 dark:bg-primary/5 shadow-lg ring-1 ring-primary/20 scale-[1.01]';
                                        indicatorClass += 'border-primary bg-primary text-white scale-110';
                                    } else {
                                        optionStyleClass += 'border-slate-100 dark:border-white/5 bg-white dark:bg-white/[0.02] hover:border-slate-200 dark:hover:border-white/10 hover:shadow-md hover:scale-[1.005]';
                                        indicatorClass += 'border-slate-200 dark:border-white/10 text-slate-400 group-hover:border-primary group-hover:text-primary';
                                    }
                                }

                                return (
                                    <label
                                        key={key}
                                        className={optionStyleClass}
                                        onClick={() => isCorrect === null && setSelectedOption(key)}
                                    >
                                        <input
                                            type="radio"
                                            name="answer"
                                            className="peer sr-only"
                                            checked={isSelected}
                                            onChange={() => { }}
                                            disabled={isCorrect !== null}
                                        />
                                        <div className="flex w-full items-center gap-4">
                                            <div className={indicatorClass}>
                                                {key}
                                            </div>
                                            <div className="text-slate-900 dark:text-gray-200 text-sm font-semibold flex-1 tracking-tight">
                                                <LatexRenderer text={String(value)} inline={true} />
                                            </div>
                                        </div>
                                        {/* Icons for Result */}
                                        {isCorrect !== null && isRightAnswer && (
                                            <div className="absolute right-6 top-1/2 -translate-y-1/2 text-green-500 drop-shadow-sm">
                                                <CheckCircle size={28} />
                                            </div>
                                        )}
                                        {isCorrect !== null && isSelected && !isRightAnswer && (
                                            <div className="absolute right-6 top-1/2 -translate-y-1/2 text-red-500 drop-shadow-sm">
                                                <XCircle size={28} />
                                            </div>
                                        )}
                                    </label>
                                );
                            })}
                        </div>
                    )}

                    {/* Action Bar */}
                    <div className="px-5 py-4 bg-slate-50/50 dark:bg-white/[0.02] border-t border-slate-100 dark:border-white/5 flex flex-wrap justify-between items-center gap-3">
                        <div className="flex gap-4">
                            {isCorrect === null ? (
                                <button
                                    onClick={handleCheck}
                                    disabled={!selectedOption}
                                    className={`px-6 py-2.5 rounded-xl text-sm font-bold shadow-lg transition-all duration-300 flex items-center gap-2 transform active:scale-95
                                            ${!selectedOption
                                            ? 'bg-slate-200 dark:bg-slate-800 text-slate-400 cursor-not-allowed'
                                            : 'bg-gradient-to-r from-primary to-blue-600 hover:to-blue-500 text-white cursor-pointer hover:shadow-primary/25 hover:-translate-y-0.5'}`}
                                >
                                    <CheckCircle size={20} />
                                    Check Answer
                                </button>
                            ) : (
                                <div className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold border-2 transition-all animate-fade-in ${isCorrect ? 'text-green-600 bg-green-50/50 border-green-200 dark:bg-green-500/10 dark:border-green-500/30' : 'text-red-600 bg-red-50/50 border-red-200 dark:bg-red-500/10 dark:border-red-500/30'}`}>
                                    {isCorrect ? <CheckCircle size={18} /> : <XCircle size={18} />}
                                    {isCorrect ? 'Correct Answer' : 'Incorrect Answer'}
                                </div>
                            )}

                            <button
                                onClick={handleShowSolutionToggle}
                                className={`px-5 py-2.5 rounded-xl text-sm font-bold transition-all duration-300 flex items-center gap-2 border-2 transform active:scale-95
                                    ${showSolution
                                        ? 'bg-slate-900 border-slate-900 text-white dark:bg-white dark:border-white dark:text-slate-900 shadow-lg'
                                        : 'bg-white dark:bg-white/5 border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/10 hover:border-slate-300 dark:hover:border-white/20'}`}
                            >
                                {showSolution ? "Hide Solution" : "Show Solution"}
                            </button>

                            <button
                                onClick={() => {
                                    setShowDiscuss(!showDiscuss);
                                    if (!showDiscuss) setShowSolution(false); // Optional: close solution when opening discuss
                                }}
                                className={`px-5 py-2.5 rounded-xl text-sm font-bold transition-all duration-300 flex items-center gap-2 border-2 transform active:scale-95
                                    ${showDiscuss
                                        ? 'bg-slate-900 border-slate-900 text-white dark:bg-white dark:border-white dark:text-slate-900 shadow-lg'
                                        : 'bg-white dark:bg-white/5 border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/10 hover:border-slate-300 dark:hover:border-white/20'}`}
                            >
                                <MessageSquare size={20} />
                                {showDiscuss ? "Hide Discussion" : "Discuss"}
                            </button>
                        </div>
                    </div>

                    {/* Discussion Section */}
                    {showDiscuss && (
                        <div className="mb-10 animate-fade-in">
                            <DiscussionSection questionId={currentQuestion.id} />
                        </div>
                    )}

                    {/* Solution Panel (Matching QuestionDetail) */}
                    {showSolution && (
                        <div className="bg-gradient-to-br from-blue-50/80 to-indigo-50/50 dark:from-primary/10 dark:to-blue-900/5 border border-blue-100 dark:border-white/10 rounded-3xl p-8 md:p-10 animate-fade-in relative overflow-hidden mb-10 shadow-2xl shadow-blue-500/5">
                            <div className={cn("relative z-10", !(isPremium || hasUsedDailySolution) && "blur-xl select-none pointer-events-none")}>
                                <div className="absolute top-0 right-0 p-8 text-blue-500/10 pointer-events-none">
                                    <Lightbulb size={120} strokeWidth={1} />
                                </div>
                                <div>
                                    <h3 className="text-xl font-extrabold text-slate-900 dark:text-white mb-8 flex items-center gap-3">
                                        <span className="bg-primary text-white p-2 rounded-xl shadow-lg shadow-primary/30">
                                            <CheckCircle size={24} />
                                        </span>
                                        Correct Answer: <span className="text-primary underline decoration-4 underline-offset-4">{currentQuestion.answer_key}</span>
                                    </h3>
                                    <div className="prose prose-blue dark:prose-invert max-w-none text-slate-900 dark:text-gray-200 space-y-10">

                                        {/* Reasoning Text */}
                                        {reasoning && (
                                            <div className="bg-white/40 dark:bg-white/5 rounded-2xl p-6 border border-white/60 dark:border-white/10 shadow-sm">
                                                <h4 className="font-bold text-xs text-blue-600 dark:text-blue-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                                                    <div className="w-1.5 h-1.5 rounded-full bg-current"></div>
                                                    Detailed Reasoning
                                                </h4>
                                                <div className="text-base leading-relaxed text-slate-800 dark:text-slate-200">
                                                    <LatexRenderer text={reasoning} />
                                                </div>
                                            </div>
                                        )}

                                        {/* Steps */}
                                        {steps.length > 0 && (
                                            <div className="bg-white/40 dark:bg-white/5 rounded-2xl p-6 border border-white/60 dark:border-white/10 shadow-sm">
                                                <h4 className="font-bold text-xs text-blue-600 dark:text-blue-400 uppercase tracking-widest mb-6 flex items-center gap-2">
                                                    <div className="w-1.5 h-1.5 rounded-full bg-current"></div>
                                                    Step-by-Step Validation
                                                </h4>
                                                <ul className="space-y-6">
                                                    {steps.map((step, idx) => (
                                                        <li key={idx} className="flex gap-4">
                                                            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500/10 dark:bg-blue-400/20 text-blue-600 dark:text-blue-400 flex items-center justify-center text-[10px] font-bold border border-blue-200 dark:border-blue-400/20">
                                                                {idx + 1}
                                                            </div>
                                                            <div className="text-slate-800 dark:text-slate-200 text-[0.95rem] leading-relaxed">
                                                                <LatexRenderer text={step} />
                                                            </div>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                        {/* Legacy fallback if no steps/reasoning but basic explanation exists */}
                                        {!reasoning && steps.length === 0 && currentQuestion.explanation && (
                                            <div className="bg-white/40 dark:bg-white/5 rounded-2xl p-6 border border-white/60 dark:border-white/10 shadow-sm">
                                                <h4 className="font-bold text-xs text-blue-600 dark:text-blue-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                                                    <div className="w-1.5 h-1.5 rounded-full bg-current"></div>
                                                    Explanation
                                                </h4>
                                                <div className="text-base leading-relaxed text-slate-800 dark:text-slate-200">
                                                    <LatexRenderer text={currentQuestion.explanation} />
                                                </div>
                                            </div>
                                        )}

                                        {!reasoning && steps.length === 0 && !currentQuestion.explanation && (
                                            <p className="italic text-gray-500">Detailed explanation coming soon.</p>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {!(isPremium || hasUsedDailySolution) && (
                                <div className="absolute inset-0 z-20 flex items-center justify-center p-6 bg-white/40 dark:bg-black/20 backdrop-blur-sm">
                                    <div className="bg-white dark:bg-slate-900 p-8 rounded-[2rem] shadow-2xl border border-slate-200 dark:border-white/10 text-center max-w-sm animate-fade-in-up">
                                        <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                            <Sparkles className="text-primary" size={32} />
                                        </div>
                                        <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Upgrade to Pro</h4>
                                        <p className="text-slate-500 dark:text-gray-400 text-sm mb-6">
                                            Unlock full step-by-step derivations and premium LaTeX explanations for every question.
                                        </p>
                                        <button
                                            onClick={onPremium}
                                            className="w-full bg-slate-900 dark:bg-white text-white dark:text-slate-900 py-3 rounded-xl font-bold shadow-lg transition-all transform hover:-translate-y-1 active:scale-95"
                                        >
                                            See Full Derivation
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Sign Up Toast Nudge for Guests */}
            {showSignUpToast && (
                <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[100] animate-fade-in-up">
                    <div className="bg-white dark:bg-card-dark rounded-2xl shadow-2xl border border-slate-200 dark:border-white/10 px-6 py-4 flex items-center gap-4 max-w-md">
                        <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center text-primary flex-shrink-0">
                            <Sparkles size={20} />
                        </div>
                        <div className="flex-1">
                            <p className="text-sm font-bold text-slate-900 dark:text-white">Sign up to save your progress!</p>
                            <p className="text-xs text-slate-500 dark:text-gray-400">Your answers won't be saved as a guest.</p>
                        </div>
                        <button
                            onClick={() => {
                                setShowSignUpToast(false);
                                window.dispatchEvent(new CustomEvent('open-auth-modal'));
                            }}
                            className="bg-primary hover:bg-blue-600 text-white text-xs font-bold px-4 py-2 rounded-xl transition-all flex-shrink-0"
                        >
                            Sign Up
                        </button>
                        <button
                            onClick={() => setShowSignUpToast(false)}
                            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 text-lg leading-none flex-shrink-0"
                        >
                            ×
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PaperAttemptView;
