import React, { useState, useEffect, useRef } from 'react';
import { api } from '../utils/api';
import LatexRenderer from './LatexRenderer';
import { ChevronRight, ChevronLeft, Info, HelpCircle } from 'lucide-react';
import GateCalculator from './GateCalculator';

// Status Enums
const STATUS = {
    NOT_VISITED: 0,
    NOT_ANSWERED: 1,
    ANSWERED: 2,
    MARKED_FOR_REVIEW: 3,
    ANSWERED_MARKED_FOR_REVIEW: 4,
};

// SVG Icons for the Legend / Palette Buttons
const StatusIcon = ({ status, number, className = '' }) => {
    switch (status) {
        case STATUS.NOT_VISITED:
            return (
                <div className={`relative flex items-center justify-center w-10 h-10 ${className}`}>
                    <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" className="absolute inset-0 drop-shadow-sm">
                        <rect width="40" height="40" rx="4" fill="#EAEAEA" stroke="#CCCCCC" />
                    </svg>
                    <span className="relative text-black font-semibold text-sm">{number}</span>
                </div>
            );
        case STATUS.NOT_ANSWERED:
            return (
                <div className={`relative flex items-center justify-center w-10 h-10 ${className}`}>
                    <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" className="absolute inset-0 drop-shadow-md">
                        <path d="M0 0 H40 V30 Q20 40 0 30 Z" fill="#E84142" />
                    </svg>
                    <span className="relative text-white font-semibold text-sm">{number}</span>
                </div>
            );
        case STATUS.ANSWERED:
            return (
                <div className={`relative flex items-center justify-center w-10 h-10 ${className}`}>
                 <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" className="absolute inset-0 drop-shadow-md">
                    <path d="M0 10 Q20 0 40 10 V40 H0 Z" fill="#29A645" />
                </svg>
                    <span className="relative text-white font-semibold text-sm">{number}</span>
                </div>
            );
        case STATUS.MARKED_FOR_REVIEW:
            return (
                <div className={`relative flex items-center justify-center w-10 h-10 ${className}`}>
                    <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" className="absolute inset-0 drop-shadow-md">
                        <circle cx="20" cy="20" r="20" fill="#75529A" />
                    </svg>
                    <span className="relative text-white font-semibold text-sm">{number}</span>
                </div>
            );
        case STATUS.ANSWERED_MARKED_FOR_REVIEW:
            return (
                <div className={`relative flex items-center justify-center w-10 h-10 ${className}`}>
                    <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" className="absolute inset-0 drop-shadow-md">
                        <circle cx="20" cy="20" r="20" fill="#75529A" />
                        <circle cx="32" cy="32" r="6" fill="#29A645" stroke="white" strokeWidth="1"/>
                    </svg>
                    <span className="relative text-white font-semibold text-sm">{number}</span>
                </div>
            );
        default:
            return null;
    }
};


const CbtExamView = ({ year, onBack, user }) => {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    // Exam state
    const [activeSection, setActiveSection] = useState('GA'); // 'GA' or 'SUBJECT'
    const [currentIndex, setCurrentIndex] = useState(0); // 0-based index within the ACTIVE section array
    
    // Status tracking map: { question_id: STATUS_INT }
    const [statuses, setStatuses] = useState({});
    
    // Selected options: { question_id: 'A' | 'B' | etc }
    const [answers, setAnswers] = useState({});
    
    // Timer
    const [timeLeftSeconds, setTimeLeftSeconds] = useState(3 * 3600); // 180 minutes

    const [showCalculator, setShowCalculator] = useState(false);

    useEffect(() => {
        const fetchPaper = async () => {
            setLoading(true);
            try {
                // Fetch full paper
                const data = await api.get('/questions', { year: year, page_size: 100 });
                // Enforce Q1 -> Q65 sort
                const sorted = data.sort((a, b) => (a.question_number || 0) - (b.question_number || 0));
                
                setQuestions(sorted);
                
                // Initialize statuses
                const initialStatuses = {};
                sorted.forEach((q, i) => {
                    // Question 1 starts as NOT_ANSWERED (because it is viewed), others NOT_VISITED
                    initialStatuses[q.question_id] = (i === 0) ? STATUS.NOT_ANSWERED : STATUS.NOT_VISITED;
                });
                setStatuses(initialStatuses);
            } catch (err) {
                console.error("Failed to fetch paper:", err);
                setError("Failed to load exam data. Please try again.");
            } finally {
                setLoading(false);
            }
        };
        fetchPaper();
    }, [year]);

    useEffect(() => {
        if (loading) return;
        const intervalId = setInterval(() => {
            setTimeLeftSeconds((prev) => (prev > 0 ? prev - 1 : 0));
        }, 1000);
        return () => clearInterval(intervalId);
    }, [loading]);

    // Data Helpers
    const gaQuestions = questions.filter(q => q.subject === 'General Aptitude' || (q.question_number >= 1 && q.question_number <= 10));
    const subjectQuestions = questions.filter(q => q.subject !== 'General Aptitude' && (q.question_number > 10));
    
    const activeQuestions = activeSection === 'GA' ? gaQuestions : subjectQuestions;
    const currentQuestion = activeQuestions[currentIndex];

    // Compute Legend Counts
    const getLegendCounts = () => {
        const counts = { [STATUS.NOT_VISITED]: 0, [STATUS.NOT_ANSWERED]: 0, [STATUS.ANSWERED]: 0, [STATUS.MARKED_FOR_REVIEW]: 0, [STATUS.ANSWERED_MARKED_FOR_REVIEW]: 0 };
        Object.values(statuses).forEach(v => {
            if (counts[v] !== undefined) counts[v]++;
        });
        return counts;
    };
    const legendCounts = getLegendCounts();

    const formatTime = (totalSeconds) => {
        const h = Math.floor(totalSeconds / 3600);
        const m = Math.floor((totalSeconds % 3600) / 60);
        const s = totalSeconds % 60;
        return [h, m, s].map(v => v < 10 ? "0" + v : v).join(":");
    };

    // Actions
    const handleOptionSelect = (key) => {
        if (!currentQuestion) return;
        setAnswers(prev => ({
            ...prev,
            [currentQuestion.question_id]: key
        }));
    };

    const moveToNext = () => {
        // Find next question in current section
        if (currentIndex < activeQuestions.length - 1) {
            handleQuestionJump(currentIndex + 1, activeSection);
        } else if (activeSection === 'GA' && subjectQuestions.length > 0) {
            // Traverse to subject section
            handleQuestionJump(0, 'SUBJECT');
        }
    };

    const handleSaveAndNext = () => {
        if (!currentQuestion) return;
        const qId = currentQuestion.question_id;
        const hasAnswer = !!answers[qId];
        
        setStatuses(prev => ({
            ...prev,
            [qId]: hasAnswer ? STATUS.ANSWERED : STATUS.NOT_ANSWERED
        }));
        
        moveToNext();
    };

    const handleMarkForReviewAndNext = () => {
        if (!currentQuestion) return;
        const qId = currentQuestion.question_id;
        const hasAnswer = !!answers[qId];
        
        setStatuses(prev => ({
            ...prev,
            [qId]: hasAnswer ? STATUS.ANSWERED_MARKED_FOR_REVIEW : STATUS.MARKED_FOR_REVIEW
        }));

        moveToNext();
    };

    const handleClearResponse = () => {
        if (!currentQuestion) return;
        const qId = currentQuestion.question_id;
        
        setAnswers(prev => {
            const next = { ...prev };
            delete next[qId];
            return next;
        });
    };

    const handleQuestionJump = (index, section) => {
        if (section !== activeSection) {
            setActiveSection(section);
        }
        setCurrentIndex(index);
        
        // Update visited status for new question if it was previously not visited
        const arr = section === 'GA' ? gaQuestions : subjectQuestions;
        const q = arr[index];
        if (q) {
            setStatuses(prev => {
                const s = prev[q.question_id];
                if (s === STATUS.NOT_VISITED) {
                    return { ...prev, [q.question_id]: STATUS.NOT_ANSWERED };
                }
                return prev;
            });
        }
    };

    const handleSubmit = () => {
        if (window.confirm("Are you sure you want to drop the exam and exit?")) {
            onBack();
        }
    };

    if (loading) {
        return <div className="flex-1 flex items-center justify-center bg-[#E5E5E5] h-screen">Loading Exam Data...</div>;
    }

    if (error || !currentQuestion) {
        return <div className="flex-1 flex items-center justify-center bg-[#E5E5E5] h-screen">{error || "No questions found"}</div>;
    }

    // Determine current user data
    const candidateName = user ? user.name || user.email.split('@')[0] : 'John Smith';
    
    // Check if current question has a selected answer
    const currentAnswer = answers[currentQuestion.question_id];

    return (
        <div className="flex flex-col h-screen w-full bg-[#E5E5E5] font-sans selection:bg-blue-200">
            {/* --- TOP HEADER --- */}
            <header className="bg-white border-b-4 border-[#1E74B0] flex flex-col drop-shadow-sm z-10 shrink-0">
                <div className="flex justify-between items-center px-4 py-2 border-b border-gray-200">
                    <div className="flex items-center gap-3">
                        <div className="font-extrabold text-2xl tracking-tighter text-[#1E74B0]">GATE 2026</div>
                        <div className="text-gray-600 text-sm font-semibold border-l-2 border-gray-300 pl-3">
                            Mock Exam
                        </div>
                    </div>
                    <div className="flex gap-4">
                        <button className="text-[#1E74B0] text-sm hover:bg-blue-50 px-3 py-1.5 rounded transition font-medium flex items-center gap-1">
                            <Info size={16}/> View Instructions
                        </button>
                    </div>
                </div>
            </header>

            {/* --- MAIN EXAM AREA --- */}
            <div className="flex flex-1 overflow-hidden">
                
                {/* --- LEFT PANEL: Questions --- */}
                <div className="flex-1 flex flex-col bg-white overflow-hidden relative border-r-4 border-[#3c8dbd]">
                    {/* Sections Tab Row */}
                    <div className="flex justify-between items-center bg-[#F2F3F5] border-b border-gray-300 pr-2">
                        <div className="flex">
                            {gaQuestions.length > 0 && (
                                <button 
                                    onClick={() => handleQuestionJump(0, 'GA')}
                                    className={`px-6 py-2.5 text-sm font-bold border-r border-[#D9D9D9] transition-colors
                                        ${activeSection === 'GA' ? 'bg-[#3c8dbd] text-white' : 'text-gray-700 hover:bg-gray-200'}`}
                                >
                                    General Aptitude
                                </button>
                            )}
                            {subjectQuestions.length > 0 && (
                                <button 
                                    onClick={() => handleQuestionJump(0, 'SUBJECT')}
                                    className={`px-6 py-2.5 text-sm font-bold border-r border-[#D9D9D9] transition-colors
                                        ${activeSection === 'SUBJECT' ? 'bg-[#3c8dbd] text-white' : 'text-gray-700 hover:bg-gray-200'}`}
                                >
                                    Aerospace Engineering
                                </button>
                            )}
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="text-sm font-bold text-gray-700">Time Left :</div>
                            <div className="bg-[#FFFFCC] border border-gray-300 px-3 py-1 font-mono font-bold text-lg text-[#D00000] rounded">
                                {formatTime(timeLeftSeconds)}
                            </div>
                            <button 
                                onClick={() => setShowCalculator(!showCalculator)} 
                                className="ml-2 text-[#E67E22] hover:text-[#D35400] transition-colors bg-white border border-[#E67E22] rounded p-1 shadow-sm flex items-center justify-center relative cursor-pointer z-10"
                                title="Virtual Calculator"
                            >
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M5 2h14a2 2 0 012 2v16a2 2 0 01-2 2H5a2 2 0 01-2-2V4a2 2 0 012-2zm0 2v16h14V4H5zm2-14h10v4H7V6zm0 6h2v2H7v-2zm4 0h2v2h-2v-2zm4 0h2v2h-2v-2zm-8 4h2v2H7v-2zm4 0h2v2h-2v-2zm4 0h2v2h-2v-2z" /></svg>
                            </button>
                        </div>
                    </div>

                    {/* Question Header */}
                    <div className="flex justify-between items-center px-4 py-2 bg-white border-b border-gray-200 shrink-0">
                        <div className="font-bold text-[#1E74B0] text-base">
                            Question No. {currentQuestion.question_number}
                        </div>
                        <div className="flex gap-4 text-sm font-medium text-gray-600">
                            <div>Question Type: <span className="font-bold text-gray-800">MCQ</span></div>
                            <div>Marks for correct answer: <span className="font-bold text-[#29A645]">{currentQuestion.marks}</span></div>
                            <div>Negative Marks: <span className="font-bold text-[#D00000]">{currentQuestion.marks === 1 ? '1/3' : '2/3'}</span></div>
                        </div>
                    </div>

                    {/* Question Content (Scrollable) */}
                    <div className="flex-1 overflow-y-auto p-6 relative bg-white">
                        <div className="prose max-w-none text-gray-800 font-medium mb-8 pb-4">
                            <LatexRenderer text={currentQuestion.question_text} />
                            {currentQuestion.question_text_latex && (
                                <div className="mt-4">
                                    <LatexRenderer text={`$$${currentQuestion.question_text_latex}$$`} block={true} />
                                </div>
                            )}
                        </div>

                        {/* Options */}
                        {currentQuestion.options && (
                            <div className="flex flex-col gap-4 mt-6">
                                {Object.entries(currentQuestion.options).filter(([k]) => k !== 'id').map(([key, value]) => (
                                    <label key={key} className="flex items-start gap-4 cursor-pointer group hover:bg-blue-50/50 p-2 rounded">
                                        <div className="mt-1 flex-shrink-0">
                                            <input 
                                                type="radio" 
                                                name={`question_${currentQuestion.question_id}`} 
                                                className="w-4 h-4 text-[#1E74B0] border-gray-400 focus:ring-[#1E74B0]"
                                                checked={currentAnswer === key}
                                                onChange={() => handleOptionSelect(key)}
                                            />
                                        </div>
                                        <div className="text-gray-800 text-sm md:text-base leading-relaxed">
                                            <span className="font-bold mr-2 text-gray-600">({key})</span>
                                            <LatexRenderer text={String(value)} inline={true} />
                                        </div>
                                    </label>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Bottom Action Bar */}
                    <div className="bg-[#EFEFEF] border-t border-gray-300 p-3 flex justify-between shrink-0 shadow-[0_-2px_5px_rgba(0,0,0,0.05)]">
                        <div className="flex gap-3">
                            <button 
                                onClick={handleMarkForReviewAndNext}
                                className="px-4 py-2 text-sm font-bold bg-white text-gray-800 border border-gray-400 rounded hover:bg-gray-100 shadow-sm"
                            >
                                Mark for Review & Next
                            </button>
                            <button 
                                onClick={handleClearResponse}
                                className="px-4 py-2 text-sm font-bold bg-white text-gray-800 border border-gray-400 rounded hover:bg-gray-100 shadow-sm"
                            >
                                Clear Response
                            </button>
                        </div>
                        <div className="flex gap-3">
                            <button 
                                onClick={() => {
                                    if (currentIndex > 0) {
                                        handleQuestionJump(currentIndex - 1, activeSection);
                                    } else if (activeSection === 'SUBJECT') {
                                        handleQuestionJump(gaQuestions.length - 1, 'GA');
                                    }
                                }}
                                disabled={activeSection === 'GA' && currentIndex === 0}
                                className="px-4 py-2 text-sm font-bold bg-white text-gray-800 border border-gray-400 rounded hover:bg-gray-100 shadow-sm disabled:opacity-50 flex items-center gap-1"
                            >
                                <ChevronLeft size={16}/> Previous
                            </button>
                            <button 
                                onClick={handleSaveAndNext}
                                className="px-6 py-2 text-sm font-bold bg-[#1E74B0] text-white border border-[#165A8A] rounded hover:bg-[#165A8A] shadow-sm flex items-center gap-1"
                            >
                                Save & Next <ChevronRight size={16}/>
                            </button>
                        </div>
                    </div>
                </div>

                {/* --- RIGHT SIDEBAR: Status & Palette --- */}
                <div className="w-72 flex flex-col bg-[#cbe3f0] border-l border-gray-300 shrink-0">
                    {/* User Profile */}
                    <div className="bg-white p-3 flex items-center gap-4 shrink-0 shadow-sm border-b">
                        <div className="w-16 h-16 bg-gray-200 border border-gray-300 shadow-inner group overflow-hidden">
                            <img src={user?.picture || "https://ui-avatars.com/api/?name=John+Smith&background=random"} alt="Candidate" className="w-full h-full object-cover" />
                        </div>
                        <div className="flex flex-col">
                            <span className="font-bold text-gray-800 text-sm">{candidateName}</span>
                        </div>
                    </div>

                    {/* Legend Section */}
                    <div className="p-3 bg-white shrink-0 shadow-sm border-b pb-4">
                        <div className="grid grid-cols-2 gap-y-3 gap-x-2">
                            <div className="flex items-center gap-2">
                                <StatusIcon status={STATUS.ANSWERED} number={legendCounts[STATUS.ANSWERED]} className="scale-75 origin-left" />
                                <span className="text-xs text-black leading-tight">Answered</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <StatusIcon status={STATUS.NOT_ANSWERED} number={legendCounts[STATUS.NOT_ANSWERED]} className="scale-75 origin-left" />
                                <span className="text-xs text-black leading-tight">Not Answered</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <StatusIcon status={STATUS.NOT_VISITED} number={legendCounts[STATUS.NOT_VISITED]} className="scale-75 origin-left" />
                                <span className="text-xs text-black leading-tight">Not Visited</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <StatusIcon status={STATUS.MARKED_FOR_REVIEW} number={legendCounts[STATUS.MARKED_FOR_REVIEW]} className="scale-75 origin-left" />
                                <span className="text-xs text-black leading-tight">Marked for Review</span>
                            </div>
                            <div className="flex items-center gap-2 col-span-2 mt-1">
                                <StatusIcon status={STATUS.ANSWERED_MARKED_FOR_REVIEW} number={legendCounts[STATUS.ANSWERED_MARKED_FOR_REVIEW]} className="scale-75 origin-left" />
                                <span className="text-xs text-black leading-tight shrink">Answered & Marked for Review (will be considered for evaluation)</span>
                            </div>
                        </div>
                    </div>

                    {/* Question Palette Section */}
                    <div className="flex-1 flex flex-col bg-[#cbe3f0] overflow-hidden">
                        <div className="bg-[#3c8dbd] text-white font-bold p-1.5 text-center text-sm shadow">
                            {activeSection === 'GA' ? 'General Aptitude' : 'Aerospace Engineering'}
                        </div>
                        <div className="flex-1 overflow-y-auto p-3">
                            <div className="font-bold text-[#1E74B0] text-sm mb-3">Choose a Question</div>
                            <div className="grid grid-cols-5 gap-y-4 gap-x-2">
                                {activeQuestions.map((q, idx) => {
                                    const qId = q.question_id;
                                    const status = statuses[qId] ?? STATUS.NOT_VISITED;
                                    const isCurrent = (idx === currentIndex);
                                    
                                    return (
                                        <button 
                                            key={qId} 
                                            onClick={() => handleQuestionJump(idx, activeSection)}
                                            className={`relative flex justify-center transform transition-transform hover:scale-105 active:scale-95`}
                                        >
                                            <StatusIcon status={status} number={q.question_number} className={isCurrent ? 'ring-2 ring-black ring-offset-1 rounded-sm' : ''} />
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    </div>

                    {/* Submit Section */}
                    <div className="p-3 bg-white shrink-0 border-t flex justify-between">
                         <button 
                            className="px-4 py-2 text-sm font-bold bg-[#EFEFEF] text-gray-800 border border-[#D9D9D9] hover:bg-[#E0E0E0] shadow-sm rounded"
                         >
                            Question Paper
                         </button>
                        <button 
                            onClick={handleSubmit}
                            className="px-6 py-2 text-sm font-bold bg-[#5BC0DE] text-white border border-[#46B8DA] hover:bg-[#31b0d5] shadow-sm rounded"
                        >
                            Exit
                        </button>
                    </div>

                </div>
            </div>
            {/* Calculator Overlay */}
            {showCalculator && <GateCalculator onClose={() => setShowCalculator(false)} />}
        </div>
    );
};

export default CbtExamView;
