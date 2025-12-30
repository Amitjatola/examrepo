import React, { useState, useEffect } from 'react';
import { X, Filter, ChevronRight } from 'lucide-react';
import { api } from '../utils/api';
import QuestionCard from './QuestionCard';

const PreviousYearPapers = ({ onQuestionSelect }) => {
    const [selectedYear, setSelectedYear] = useState(2008); // Default to 2008 as per user data
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(false);

    // Years with available questions in DB (2007, 2008, 2025)
    // Show all years but only those with data will have questions
    const years = [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007];

    useEffect(() => {
        const fetchQuestions = async () => {
            setLoading(true);
            try {
                // Fetch all questions for the year.
                // Note: The API supports filtering by year.
                const data = await api.get('/questions', { year: selectedYear });
                setQuestions(data);
            } catch (err) {
                console.error("Failed to fetch questions:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchQuestions();
    }, [selectedYear]);

    // Helper to extract question number from question_id (e.g., GATE_AE_2008_Q01 -> 1)
    const getQuestionNumber = (q) => {
        const match = q.question_id?.match(/Q(\d+)/i);
        return match ? parseInt(match[1], 10) : 0;
    };

    // Group questions by subject and sort by question number within each group
    const questionsBySubject = questions.reduce((acc, q) => {
        const subject = q.subject || 'General';
        if (!acc[subject]) acc[subject] = [];
        acc[subject].push(q);
        return acc;
    }, {});

    // Sort each subject's questions by question number
    Object.keys(questionsBySubject).forEach(subject => {
        questionsBySubject[subject].sort((a, b) => getQuestionNumber(a) - getQuestionNumber(b));
    });

    return (
        <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark scroll-smooth h-full">
            <div className="max-w-[1200px] mx-auto p-8 space-y-8">
                {/* Page Heading */}
                <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-gray-400 mb-1">
                        <span>Practice</span>
                        <ChevronRight size={16} />
                        <span className="text-primary font-medium">Previous Year Questions</span>
                    </div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white font-display">GATE Aerospace Papers</h1>
                    <p className="text-slate-500 dark:text-gray-400 max-w-2xl">Access authentic previous year papers arranged topic-wise. Master the exam pattern by solving actual questions.</p>
                </div>

                {/* Year Tabs Selector */}
                <div className="sticky top-0 z-10 bg-background-light/95 dark:bg-background-dark/95 backdrop-blur-sm pt-4 pb-2 -mx-4 px-4 border-b border-[#dbe0e6] dark:border-border-dark">
                    <div className="flex items-end gap-8 overflow-x-auto no-scrollbar">
                        {years.map((year) => (
                            <button
                                key={year}
                                onClick={() => setSelectedYear(year)}
                                className={`flex flex-col items-center justify-center pb-3 border-b-[3px] px-2 transition-all cursor-pointer ${selectedYear === year
                                    ? 'border-primary text-primary'
                                    : 'border-transparent text-slate-500 hover:text-slate-900 dark:text-gray-400 dark:hover:text-white'
                                    }`}
                            >
                                <span className={`text-base tracking-tight ${selectedYear === year ? 'font-bold' : 'font-medium'}`}>{year}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Filters & Stats Row */}
                <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="flex flex-wrap gap-2">
                        {/* Active Chip */}
                        <button className="flex h-9 items-center justify-center gap-2 rounded-full bg-slate-900 dark:bg-white text-white dark:text-slate-900 pl-4 pr-3 text-sm font-medium transition-transform active:scale-95 cursor-pointer">
                            All Subjects
                            <X size={18} />
                        </button>
                        <div className="w-[1px] h-6 bg-gray-300 dark:bg-gray-700 mx-2 self-center"></div>
                        <button className="flex h-9 items-center justify-center gap-2 rounded-full border border-dashed border-[#dbe0e6] dark:border-gray-700 text-slate-500 dark:text-gray-400 hover:text-primary hover:border-primary pl-3 pr-4 text-sm font-medium transition-colors cursor-pointer">
                            <Filter size={18} />
                            Difficulty
                        </button>
                    </div>
                    <div className="text-sm text-slate-500 dark:text-gray-500 font-medium">
                        Showing {questions.length} questions from {selectedYear}
                    </div>
                </div>

                {/* Content Section: Dynamic Grouping */}
                {Object.keys(questionsBySubject).length > 0 ? (
                    Object.entries(questionsBySubject).map(([subject, subjectQuestions]) => (
                        <section key={subject} className="space-y-4">
                            <div className="flex items-center gap-2 mb-2">
                                <h2 className="text-xl font-bold text-slate-900 dark:text-white font-display">{subject}</h2>
                                <span className="bg-blue-100 dark:bg-blue-900/30 text-primary text-xs font-bold px-2 py-0.5 rounded-full">{subjectQuestions.length} Qs</span>
                            </div>
                            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                                {subjectQuestions.map(q => (
                                    <QuestionCard
                                        key={q.id}
                                        question={q} // Passing the full object as adapter inside Card handles it
                                        onClick={() => onQuestionSelect(q)}
                                    />
                                ))}
                            </div>
                        </section>
                    ))
                ) : (
                    <div className="py-20 text-center text-gray-500">
                        {loading ? "Loading questions..." : "No questions found for this year."}
                    </div>
                )}


                <div className="flex justify-center py-8">
                    <button className="px-6 py-2.5 rounded-lg border border-[#dbe0e6] dark:border-gray-700 text-sm font-bold text-slate-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-white transition-all cursor-pointer">
                        Load More Questions
                    </button>
                </div>
            </div>
        </div>
    );
}



export default PreviousYearPapers;
