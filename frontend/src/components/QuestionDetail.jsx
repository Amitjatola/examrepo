
import React, { useState, useEffect } from 'react';
import {
    Signal,
    CheckCircle, Eye, ChevronLeft, History, Sparkles, Printer,
    CalendarClock, RefreshCw,
} from 'lucide-react';
import { api } from '../utils/api';
import LatexRenderer from './LatexRenderer';
import { useAuth } from '../context/AuthContext';
import { TierViews } from './premium/TierViews';
import { cn } from './premium/ui';
import HintSteps from './HintSteps';
import QuestionNavRail from './QuestionNavRail';
import FormulaSheetPrint from './FormulaSheetPrint';
import DiscussionSection from './DiscussionSection';

const QuestionDetail = ({
    questionId,
    onBack,
    onOpenPremium,
    navigatorQuestionIds,
    onNavigatorQuestionSelect,
    bookmarkSlot,
}) => {
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
    const [showFormulaPrint, setShowFormulaPrint] = useState(false);
    const [revisionInfo, setRevisionInfo] = useState(null);
    const [revLoading, setRevLoading] = useState(false);
    const [revBusy, setRevBusy] = useState(false);

    const startTimeRef = React.useRef(Date.now());
    const { user, isPremium } = useAuth();

    useEffect(() => {
        if (!navigatorQuestionIds?.length || !questionId || !onNavigatorQuestionSelect) return undefined;
        const handleKeyDown = (event) => {
            const tag = event.target?.tagName?.toLowerCase?.();
            if (tag === 'input' || tag === 'textarea' || event.target?.isContentEditable) return;
            const idx = navigatorQuestionIds.indexOf(questionId);
            if (idx < 0) return;
            if (event.key === 'j' || event.key === 'ArrowDown') {
                event.preventDefault();
                const next = navigatorQuestionIds[idx + 1];
                if (next) onNavigatorQuestionSelect(next);
            }
            if (event.key === 'k' || event.key === 'ArrowUp') {
                event.preventDefault();
                const prev = navigatorQuestionIds[idx - 1];
                if (prev) onNavigatorQuestionSelect(prev);
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [navigatorQuestionIds, questionId, onNavigatorQuestionSelect]);

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

    useEffect(() => {
        const loadRevision = async () => {
            if (!user || !question?.question_id) {
                setRevisionInfo(null);
                return;
            }
            setRevLoading(true);
            try {
                const r = await api.getRevisionState(question.question_id);
                setRevisionInfo(r);
            } catch (err) {
                if (err?.status === 404) {
                    setRevisionInfo(null);
                } else {
                    console.error('Revision state load failed:', err);
                    setRevisionInfo(null);
                }
            } finally {
                setRevLoading(false);
            }
        };
        loadRevision();
    }, [user, question?.question_id]);

    const handleToggleRevision = async () => {
        if (!user || !question?.question_id) return;
        setRevBusy(true);
        try {
            if (revisionInfo) {
                await api.removeFromRevision(question.question_id);
                setRevisionInfo(null);
            } else {
                const r = await api.addToRevision(question.question_id, 'medium');
                setRevisionInfo(r);
            }
        } catch (err) {
            console.error('Revision toggle failed:', err);
        } finally {
            setRevBusy(false);
        }
    };

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
    const tier1 = question?.tier_1_core_research || {};
    // Steps are in tier_1_core_research.explanation.step_by_step
    const explanation = tier1?.explanation || question?.explanation || {};
    const steps = (Array.isArray(explanation?.step_by_step) ? explanation.step_by_step : [])
        .filter(s => s && typeof s === 'string' && s.trim() !== "");
    // Reasoning is in tier_1_core_research.answer_validation.reasoning
    const validation = tier1?.answer_validation || {};
    const reasoning = validation?.reasoning || "";

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
            <div className="flex flex-row gap-3 md:gap-4 max-w-[1400px] w-full mx-auto">
                <QuestionNavRail
                    questionIds={navigatorQuestionIds}
                    activeQuestionId={questionId}
                    onSelectQuestionId={onNavigatorQuestionSelect}
                    title="Paper"
                />
                <div className="flex-1 min-w-0 flex flex-col gap-6 pb-20 max-w-[49.28rem] mx-auto w-full">
                {/* Column max-w: +10% vs 44.8rem; card sections use ~95% vertical padding vs prior */}
                <div className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-[#e5e7eb] dark:border-border-dark overflow-hidden">
                    {/* Card Header / Meta */}
                    <div className="px-5 md:px-6 py-[0.95rem] border-b border-[#f0f2f4] dark:border-border-dark flex flex-wrap justify-between items-center gap-3">
                        <div className="space-y-1.5 min-w-0">
                            <h2 className="text-slate-900 dark:text-white text-xl md:text-[1.35rem] font-bold leading-tight font-display truncate">{question?.question_id || 'Question'}</h2>
                            <p className="text-slate-500 dark:text-gray-400 text-xs">
                                {question?.question_type || 'N/A'} • {question?.marks || 0} Marks • Q{question?.question_number ?? '—'} • {question?.subject || 'Subject'}
                            </p>
                        </div>
                        <div className="flex gap-2 flex-wrap">
                            <div className={`flex h-6 items-center justify-center gap-x-1.5 rounded-full px-2.5 border ${diffStyles.bg} ${diffStyles.border}`}>
                                <Signal size={14} className={diffStyles.icon} />
                                <p className={`${diffStyles.text} text-[10px] font-semibold uppercase tracking-wide`}>{question?.difficulty_level || 'Medium'}</p>
                            </div>
                            <div className="flex h-6 items-center justify-center gap-x-1.5 rounded-full bg-[#f0f2f4] dark:bg-landing-bg-dark/50 px-2.5">
                                <p className="text-slate-900 dark:text-gray-200 text-[10px] font-semibold uppercase tracking-wide">Year {question?.year || 'N/A'}</p>
                            </div>
                            {question?.source && (
                                <div className="flex h-6 items-center justify-center gap-x-1.5 rounded-full bg-blue-50 dark:bg-blue-900/20 px-2.5 border border-blue-100 dark:border-blue-900/30">
                                    <p className="text-blue-700 dark:text-blue-300 text-[10px] font-semibold uppercase tracking-wide">{question.source}</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Question Body */}
                    <div className="px-5 md:px-6 py-[1.1875rem]">
                        <div className="text-slate-900 dark:text-gray-200 text-base leading-relaxed font-normal">
                            <LatexRenderer text={question?.question_text_latex || question?.question_text || "No question text available."} />
                        </div>
                    </div>

                    {/* Answer Options */}
                    {question?.options && typeof question.options === 'object' && !Array.isArray(question.options) && (
                        <div className="px-5 md:px-6 pb-[1.425rem] flex flex-col gap-[0.475rem]">
                            {Object.entries(question.options).map(([key, value]) => {
                                let optionStyleClass = `group relative flex cursor-pointer rounded-lg border p-[0.7125rem] transition-all `;
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
                                        <div className="flex w-full items-center gap-3">
                                            <div className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 text-[10px] font-bold transition-colors ${indicatorClass}`}>
                                                {key}
                                            </div>
                                            <div className="text-slate-900 dark:text-gray-200 text-sm font-medium">
                                                <LatexRenderer text={value} />
                                            </div>
                                        </div>

                                        {/* Feedback Icons */}
                                        {isChecked && key === question.answer_key && (
                                            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-green-600">
                                                <CheckCircle size={20} />
                                            </div>
                                        )}
                                        {isChecked && selectedOption === key && key !== question.answer_key && (
                                            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-red-500 font-bold text-lg">
                                                ✕
                                            </div>
                                        )}
                                        {!isChecked && selectedOption === key && (
                                            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-primary">
                                                <CheckCircle size={20} />
                                            </div>
                                        )}
                                    </label>
                                );
                            })}
                        </div>
                    )}

                    {steps.length > 0 && (
                        <div className="px-5 md:px-6 pb-[0.7125rem]">
                            <HintSteps
                                key={question.question_id}
                                steps={steps}
                                isPremium={isPremium}
                                questionKey={question.question_id}
                                onUpgrade={onOpenPremium}
                            />
                        </div>
                    )}

                    {/* Actions Toolbar: primary row + optional bookmark row */}
                    <div className="px-5 md:px-6 py-[0.7125rem] bg-gray-50 dark:bg-landing-bg-dark/30 border-t border-[#e5e7eb] dark:border-border-dark flex flex-col gap-[0.59375rem]">
                        <div className="flex flex-wrap items-center justify-between gap-2 gap-y-2">
                            <div className="flex gap-2 flex-wrap items-center">
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
                                        className={`px-4 py-2 rounded-lg text-xs font-semibold shadow-sm transition-all flex items-center gap-1.5 
                                            ${!selectedOption
                                                ? 'bg-gray-300 dark:bg-gray-700 text-gray-500 cursor-not-allowed'
                                                : 'bg-primary hover:bg-blue-600 text-white cursor-pointer'}`}
                                    >
                                        <CheckCircle size={16} />
                                        Check Answer
                                    </button>
                                ) : (
                                    <div className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold border ${isCorrect ? 'text-green-700 bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800' : 'text-red-700 bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800'}`}>
                                        {isCorrect ? <CheckCircle size={16} /> : <span className="font-bold">✕</span>}
                                        {isCorrect ? 'Correct Answer' : 'Incorrect Answer'}
                                    </div>
                                )}

                                <button
                                    type="button"
                                    onClick={handleShowSolutionToggle}
                                    className="bg-white dark:bg-card-dark border border-[#e5e7eb] dark:border-border-dark hover:bg-gray-50 dark:hover:bg-white/5 text-slate-900 dark:text-white px-3 py-2 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 cursor-pointer"
                                >
                                    <Eye size={16} />
                                    {showSolution ? 'Hide Solution' : 'Show Solution'}
                                </button>
                            </div>
                            <div className="flex items-center gap-1.5 flex-wrap shrink-0">
                                <button
                                    type="button"
                                    onClick={() => setShowFormulaPrint(true)}
                                    className="bg-white dark:bg-card-dark border border-[#e5e7eb] dark:border-border-dark hover:bg-gray-50 dark:hover:bg-white/5 text-slate-900 dark:text-white px-2.5 py-2 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 cursor-pointer"
                                    aria-label="Print formula sheet for this question"
                                >
                                    <Printer size={16} />
                                    <span className="hidden sm:inline">Formulas</span>
                                </button>
                                <div className="h-5 w-px bg-gray-300 dark:bg-gray-600 mx-0.5" aria-hidden />
                                <button
                                    type="button"
                                    onClick={onBack}
                                    className="flex items-center gap-1 text-slate-500 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white px-2.5 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-white/10 transition-colors cursor-pointer"
                                >
                                    <ChevronLeft size={18} />
                                    <span className="text-xs font-medium hidden sm:inline">Back</span>
                                </button>
                            </div>
                        </div>
                        {user ? (
                            <div className="border-t border-[#e5e7eb] dark:border-border-dark pt-[0.7125rem] w-full min-w-0 space-y-3">
                                <div className="flex flex-wrap items-center justify-between gap-3">
                                    <div className="flex items-start gap-2 min-w-0">
                                        <CalendarClock size={18} className="text-primary shrink-0 mt-0.5" aria-hidden />
                                        <div className="min-w-0">
                                            <p className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wide">
                                                Spaced revision
                                            </p>
                                            {revLoading ? (
                                                <p className="text-xs text-slate-500 dark:text-gray-400 mt-0.5">Loading…</p>
                                            ) : revisionInfo ? (
                                                <p className="text-xs text-slate-600 dark:text-gray-300 mt-0.5">
                                                    Next review:{' '}
                                                    {revisionInfo.next_revision_at
                                                        ? new Date(revisionInfo.next_revision_at).toLocaleString()
                                                        : '—'}
                                                    {typeof revisionInfo.interval_days === 'number' ? (
                                                        <span className="text-slate-400 dark:text-slate-500">
                                                            {' '}
                                                            · interval {revisionInfo.interval_days}d · ease{' '}
                                                            {revisionInfo.ease_factor}
                                                        </span>
                                                    ) : null}
                                                </p>
                                            ) : (
                                                <p className="text-xs text-slate-500 dark:text-gray-400 mt-0.5">
                                                    Add this question to your SM-2 revision queue.
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={handleToggleRevision}
                                        disabled={revBusy || revLoading}
                                        className="inline-flex items-center gap-2 rounded-lg border border-[#e5e7eb] dark:border-border-dark bg-white dark:bg-card-dark px-3 py-2 text-xs font-semibold text-slate-800 dark:text-white hover:bg-slate-50 dark:hover:bg-white/10 disabled:opacity-50 cursor-pointer shrink-0"
                                        aria-label={revisionInfo ? 'Remove from revision queue' : 'Schedule revision'}
                                    >
                                        <RefreshCw size={14} className={revBusy ? 'animate-spin' : ''} aria-hidden />
                                        {revisionInfo ? 'Remove from revision' : 'Schedule revision'}
                                    </button>
                                </div>
                                {bookmarkSlot ? <div className="min-w-0">{bookmarkSlot}</div> : null}
                            </div>
                        ) : null}
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
                                        type="button"
                                        onClick={() => onOpenPremium?.()}
                                        className="w-full bg-primary hover:bg-blue-600 text-white py-3 rounded-xl font-bold shadow-lg shadow-primary/20 transition-all transform hover:-translate-y-1 active:scale-95"
                                    >
                                        Upgrade to Pro
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                <TierViews question={question} />

                <DiscussionSection questionId={question?.id} />

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
            </div>

            <FormulaSheetPrint open={showFormulaPrint} onClose={() => setShowFormulaPrint(false)} question={question} />
        </div>
    );
};

export default QuestionDetail;


