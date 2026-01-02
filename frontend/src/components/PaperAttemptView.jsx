
import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import QuestionCard from './QuestionCard'; // We might reuse or adapt this, but the design is specific here
import { ChevronLeft, ChevronRight, CheckCircle, XCircle, Lightbulb, Flag, Bookmark } from 'lucide-react';
import LatexRenderer from './LatexRenderer';

// A specialized Question View for the Year-based attempt flow
const PaperAttemptView = ({ year, onBack }) => {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [showSolution, setShowSolution] = useState(false);
    const [selectedOption, setSelectedOption] = useState(null);
    const [isCorrect, setIsCorrect] = useState(null);

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
    }, [currentIndex]);

    const currentQuestion = questions[currentIndex];
    const totalQuestions = questions.length;
    const progress = totalQuestions > 0 ? Math.round(((currentIndex + 1) / totalQuestions) * 100) : 0;

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

        // Record Attempt
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

    if (loading) {
        return (
            <div className="flex-1 flex justify-center items-center h-full text-slate-500">
                <span className="loading-spinner">Loading Paper...</span>
            </div>
        );
    }

    if (!currentQuestion) {
        return (
            <div className="flex-1 flex flex-col justify-center items-center h-full text-slate-500 gap-4">
                <p>No questions found for {year}.</p>
                <button onClick={onBack} className="text-primary hover:underline">Go Back</button>
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
            <div className="sticky top-0 z-10 bg-background-light/95 dark:bg-background-dark/95 backdrop-blur-md border-b border-border-light dark:border-border-dark px-6 py-3 flex items-center justify-between transition-colors">
                <nav className="flex items-center text-sm font-medium text-slate-500 dark:text-slate-400">
                    <span className="hover:text-primary transition-colors cursor-pointer" onClick={onBack}>Paper {year}</span>
                    <ChevronRight size={16} className="mx-2 text-slate-400" />
                    <span className="text-slate-900 dark:text-white">Question {currentQuestion.question_number}</span>
                </nav>
                <div className="flex items-center gap-4">
                    <div className="flex flex-col items-end mr-2 hidden sm:flex">
                        <div className="text-xs text-slate-500 dark:text-slate-400 font-medium mb-1">
                            {currentIndex + 1} of {totalQuestions}
                        </div>
                        <div className="w-32 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-primary rounded-full transition-all duration-300"
                                style={{ width: `${progress}%` }}
                            ></div>
                        </div>
                    </div>
                    <button className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors rounded-full hover:bg-slate-100 dark:hover:bg-slate-800">
                        <Flag size={18} />
                    </button>
                    <button className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors rounded-full hover:bg-slate-100 dark:hover:bg-slate-800">
                        <Bookmark size={18} />
                    </button>
                </div>
            </div>

            {/* Scrollable Content Container */}
            <div className="flex-1 overflow-y-auto scroll-smooth">
                <div className="w-full max-w-4xl mx-auto px-4 sm:px-8 py-8 flex flex-col pb-20">

                    {/* Question Card (Reflecting QuestionDetail Style) */}
                    <div className="bg-white dark:bg-card-dark rounded-xl shadow-sm border border-[#e5e7eb] dark:border-border-dark overflow-hidden mb-6">

                        {/* Card Header / Meta */}
                        <div className="px-6 md:px-8 py-5 border-b border-[#f0f2f4] dark:border-border-dark flex flex-wrap justify-between items-center gap-4">
                            <div>
                                <h2 className="text-slate-900 dark:text-white text-2xl font-bold leading-tight tracking-tight mb-2">Question {currentQuestion.question_number}</h2>
                                <span className="text-slate-500 dark:text-gray-400 text-sm mt-1">{currentQuestion.subject || "General"} • {currentQuestion.marks} Mark{currentQuestion.marks !== 1 ? 's' : ''}</span>
                            </div>
                            <div className="flex gap-2 flex-wrap">
                                {/* Difficulty Badge */}
                                <div className={`flex h-7 items-center justify-center gap-x-1.5 rounded-full px-3 border ${diffStyles.bg} ${diffStyles.border}`}>
                                    <span className={`${diffStyles.text} text-xs font-semibold uppercase tracking-wide`}>{currentQuestion.difficulty_level || 'Medium'}</span>
                                </div>
                                <div className="flex items-center gap-2 text-xs text-slate-400 font-mono bg-slate-50 dark:bg-slate-900 px-2 py-1 rounded border border-slate-100 dark:border-slate-800 hidden sm:flex">
                                    <span>ID: {currentQuestion.question_id}</span>
                                </div>
                            </div>
                        </div>

                        {/* Question Body */}
                        <div className="px-6 md:px-8 py-6">
                            <div className="text-slate-900 dark:text-gray-200 text-lg leading-relaxed font-normal prose dark:prose-invert max-w-none">
                                <LatexRenderer text={currentQuestion.question_text} />
                                {currentQuestion.question_text_latex && (
                                    <div className="mt-4 p-4 bg-slate-50 dark:bg-[#131728] rounded-lg border border-slate-100 dark:border-slate-800 flex justify-center items-center overflow-x-auto">
                                        <LatexRenderer text={`$$${currentQuestion.question_text_latex}$$`} block={true} />
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Options */}
                        {currentQuestion.options && (
                            <div className="px-6 md:px-8 pb-8 flex flex-col gap-3">
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

                                    let optionStyleClass = `group relative flex cursor-pointer rounded-lg border p-4 transition-all `;
                                    let indicatorClass = "";

                                    if (isCorrect !== null) {
                                        // CHECKED STATE
                                        if (isRightAnswer) {
                                            // Always highlight correct answer in green if checked
                                            optionStyleClass += 'border-green-500 bg-green-50 dark:bg-green-900/20 shadow-md';
                                            indicatorClass = 'border-green-500 bg-green-500 text-white';
                                        } else if (isSelected) {
                                            // Selected but Wrong -> Red
                                            optionStyleClass += 'border-red-500 bg-red-50 dark:bg-red-900/20 shadow-md';
                                            indicatorClass = 'border-red-500 bg-red-500 text-white';
                                        } else {
                                            // Others -> Dimmed
                                            optionStyleClass += 'border-[#e5e7eb] dark:border-border-dark bg-white dark:bg-card-dark opacity-60';
                                            indicatorClass = 'border-[#cbd5e1] text-[#64748b]';
                                        }
                                    } else {
                                        // NORMAL STATE
                                        if (isSelected) {
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
                                                <div className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 text-xs font-bold transition-colors ${indicatorClass}`}>
                                                    {key}
                                                </div>
                                                <div className="text-slate-900 dark:text-gray-200 text-base font-medium flex-1">
                                                    <LatexRenderer text={String(value)} inline={true} />
                                                </div>
                                            </div>
                                            {/* Icons for Result */}
                                            {isCorrect !== null && isRightAnswer && (
                                                <div className="absolute right-4 top-1/2 -translate-y-1/2 text-green-600">
                                                    <CheckCircle size={24} />
                                                </div>
                                            )}
                                            {isCorrect !== null && isSelected && !isRightAnswer && (
                                                <div className="absolute right-4 top-1/2 -translate-y-1/2 text-red-500 font-bold text-xl">
                                                    <XCircle size={24} />
                                                </div>
                                            )}
                                            {isCorrect === null && isSelected && (
                                                <div className="absolute right-4 top-1/2 -translate-y-1/2 text-primary">
                                                    <CheckCircle size={24} />
                                                </div>
                                            )}
                                        </label>
                                    );
                                })}
                            </div>
                        )}

                        {/* Action Bar */}
                        <div className="px-6 md:px-8 py-4 bg-gray-50 dark:bg-landing-bg-dark/30 border-t border-[#e5e7eb] dark:border-border-dark flex flex-wrap justify-between items-center gap-4">
                            <div className="flex gap-3">
                                {isCorrect === null ? (
                                    <button
                                        onClick={handleCheck}
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
                                        {isCorrect ? <CheckCircle size={18} /> : <span className="font-bold"><XCircle size={18} /></span>}
                                        {isCorrect ? 'Correct Answer' : 'Incorrect Answer'}
                                    </div>
                                )}

                                <button
                                    onClick={() => setShowSolution(!showSolution)}
                                    className="bg-white dark:bg-card-dark border border-[#e5e7eb] dark:border-border-dark hover:bg-gray-50 dark:hover:bg-white/5 text-slate-900 dark:text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2 cursor-pointer"
                                >
                                    <Lightbulb size={18} />
                                    {showSolution ? "Hide Solution" : "Show Solution"}
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Solution Panel (Matching QuestionDetail) */}
                    {showSolution && (
                        <div className="bg-blue-50/50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-900/20 rounded-xl p-6 md:p-8 animate-fade-in relative overflow-hidden mb-8">
                            <div className="relative z-10">
                                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                                    <CheckCircle className="text-primary" size={24} />
                                    Correct Answer: {currentQuestion.answer_key}
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
                                    {/* Legacy fallback if no steps/reasoning but basic explanation exists */}
                                    {!reasoning && steps.length === 0 && currentQuestion.explanation && (
                                        <div>
                                            <h4 className="font-semibold text-sm text-blue-800 dark:text-blue-300 uppercase tracking-wide mb-2">Explanation</h4>
                                            <div className="text-base leading-relaxed text-gray-800 dark:text-gray-200">
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
                    )}

                    {/* Footer Navigation */}
                    <div className="flex justify-between items-center">
                        <button
                            onClick={handlePrev}
                            disabled={currentIndex === 0}
                            className={`flex items-center gap-3 px-5 py-3 rounded-lg bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark transition-all group w-[140px] justify-between
                                ${currentIndex === 0 ? 'opacity-50 cursor-not-allowed' : 'hover:border-slate-300 dark:hover:border-slate-600 hover:shadow-soft'}`}
                        >
                            <ChevronLeft size={20} className="text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-200" />
                            <div className="text-right hidden sm:block">
                                <div className="text-[10px] text-slate-400 uppercase font-semibold tracking-wider">Previous</div>
                            </div>
                        </button>

                        <button
                            onClick={handleNext}
                            disabled={currentIndex === totalQuestions - 1}
                            className={`flex items-center gap-3 px-5 py-3 rounded-lg bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark transition-all group w-[140px] justify-between
                                ${currentIndex === totalQuestions - 1 ? 'opacity-50 cursor-not-allowed' : 'hover:border-slate-300 dark:hover:border-slate-600 hover:shadow-soft'}`}
                        >
                            <div className="text-left hidden sm:block">
                                <div className="text-[10px] text-slate-400 uppercase font-semibold tracking-wider">Next</div>
                            </div>
                            <ChevronRight size={20} className="text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-200" />
                        </button>
                    </div>

                </div>
            </div>
        </div>
    );
};

export default PaperAttemptView;
