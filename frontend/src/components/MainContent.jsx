import React, { useState, useEffect, useCallback } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import SearchBox from './SearchBox';
import QuestionCard from './QuestionCard';
import SkeletonCard from './SkeletonCard';
import PreviousYearPapers from './PreviousYearPapers';
import QuestionDetail from './QuestionDetail';
import YearSelection from './YearSelection';
import LandingPage from './LandingPage';
import AuthModal from './AuthModal';
import Dashboard from './Dashboard';
import { useTheme } from '../hooks/useTheme';
import { api } from '../utils/api';
import { useAuth } from '../context/AuthContext';

function MainContent() {
    const { theme, toggleTheme } = useTheme();
    const { openLogin, openRegister, user, logout } = useAuth();
    const [isZenMode, setIsZenMode] = useState(typeof window !== 'undefined' ? window.innerWidth < 1024 : false);

    // Persist app state to localStorage for page refresh support
    const getInitialState = () => {
        try {
            const saved = localStorage.getItem('aerogate_state');
            if (saved) {
                return JSON.parse(saved);
            }
        } catch (e) {
            console.error('Failed to parse saved state:', e);
        }
        return null;
    };

    const savedState = getInitialState();

    const [activeTab, setActiveTab] = useState(savedState?.activeTab || 'home');
    const [view, setView] = useState(savedState?.view || 'landing');
    const [query, setQuery] = useState(savedState?.query || '');
    const [loading, setLoading] = useState(false);

    // Syllabus State
    const [syllabusTree, setSyllabusTree] = useState({});
    const [selectedSubject, setSelectedSubject] = useState(savedState?.selectedSubject || null);
    const [selectedTopic, setSelectedTopic] = useState(savedState?.selectedTopic || null);
    const [selectedQuestionId, setSelectedQuestionId] = useState(savedState?.selectedQuestionId || null);

    const toggleZenMode = () => setIsZenMode(!isZenMode);
    const [results, setResults] = useState([]);
    const [error, setError] = useState(null);
    const [total, setTotal] = useState(0);

    // Save state to localStorage when it changes
    useEffect(() => {
        const stateToSave = {
            view,
            activeTab,
            query,
            selectedSubject,
            selectedTopic,
            selectedQuestionId,
        };
        localStorage.setItem('aerogate_state', JSON.stringify(stateToSave));
    }, [view, activeTab, query, selectedSubject, selectedTopic, selectedQuestionId]);

    // Handle resize to auto-hide sidebar on mobile
    useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth < 1024) {
                setIsZenMode(true);
            } else {
                setIsZenMode(false);
            }
        };

        // We only want to set this on resize, but maybe not override user preference too aggressively?
        // Actually for a simple fix, let's just use the initial state. 
        // Adding a forced listener overrides user toggle if they resize slightly. 
        // Let's skip the resize listener for now as the initial state fix covers the "loading properly" request.
    }, []);

    // Re-run search on page load if we have a saved query but no results
    useEffect(() => {
        const restoreSearch = async () => {
            if (query && results.length === 0 && (view === 'results' || view === 'years') && !loading) {
                setLoading(true);
                setError(null);
                try {
                    const data = await api.get('/search', { q: query });
                    setResults(data.questions);
                    setTotal(data.total);
                } catch (err) {
                    setError(`Error: ${err.message}. Make sure the backend is running.`);
                } finally {
                    setLoading(false);
                }
            }
        };
        restoreSearch();
        // Only run on initial mount with saved state
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // If user is logged in, maybe skip landing? 
    // For now, let's keep landing until they click "Start" or search.
    // Or if they login successfully, we switch to home.
    useEffect(() => {
        if (user && view === 'landing') {
            // setView('home'); 
            // Optional: Auto-redirect if logged in. 
            // But maybe they want to see the landing page aesthetics.
            // Let's leave it manual for now.
        }
    }, [user, view]);

    const performSearch = useCallback(async (searchQuery) => {
        setQuery(searchQuery); // Sync query state

        if (!searchQuery) {
            setResults([]);
            setTotal(0);
            // Revert to the default view for the current tab
            setView(activeTab === 'pyq' ? 'years' : 'home');
            return;
        }

        setView('results'); // Switch to results view
        setLoading(true);
        setError(null);

        try {
            const data = await api.get('/search', { q: searchQuery });
            setResults(data.questions);
            setTotal(data.total);
        } catch (err) {
            setError(`Error: ${err.message}. Make sure the backend is running.`);
        } finally {
            setLoading(false);
        }
    }, [activeTab]);

    const fetchSyllabus = useCallback(async () => {
        try {
            const data = await api.get('/questions/syllabus');
            setSyllabusTree(data);
        } catch (err) {
            console.error("Failed to fetch syllabus:", err);
        }
    }, []);

    useEffect(() => {
        if (activeTab === 'concepts') {
            fetchSyllabus();
        }
    }, [activeTab, fetchSyllabus]);

    const handleTabChange = (tabId) => {
        setActiveTab(tabId);
        setResults([]);
        setQuery('');

        if (tabId === 'home') {
            setView('home');
        } else if (tabId === 'year_select') {
            setView('year_select');
        } else if (tabId === 'concepts') {
            setView('syllabus-subjects');
            setSelectedSubject(null);
            setSelectedTopic(null);
        }
    };

    const handleYearClick = (year) => {
        performSearch(year.toString());
    };

    const handleSubjectClick = (subject) => {
        setSelectedSubject(subject);
        setView('syllabus-topics');
    };

    const handleTopicClick = (topic) => {
        setSelectedTopic(topic);
        performSearch(topic); // Search using the topic name
    };

    const handleBack = () => {
        if (view === 'question-detail') {
            // Basic history management
            if (activeTab === 'year_select') setView('years');
            else if (activeTab === 'concepts') setView('syllabus-topics');
            else setView('home');
        }
    };

    // Construct Breadcrumbs
    const getBreadcrumbs = () => {
        const crumbs = [];

        if (activeTab === 'year_select') {
            crumbs.push({ label: 'Practice by Year', onClick: () => setView('year_select') });
            if (view === 'years' && query) {
                crumbs.push({ label: query, onClick: () => { /* Already here */ } });
            }
        } else if (activeTab === 'concepts') {
            crumbs.push({ label: 'Syllabus', onClick: () => setView('syllabus-subjects') });
            if (selectedSubject) {
                crumbs.push({ label: selectedSubject, onClick: () => setView('syllabus-topics') });
            }
            if (selectedTopic) {
                crumbs.push({ label: selectedTopic, onClick: () => { /* Already here */ } });
            }
        }

        if (view === 'question-detail') {
            crumbs.push({ label: `Question`, onClick: () => { } });
        }

        return crumbs;
    };

    // Helper to determine what Main content to render
    const renderMainContent = () => {
        if (view === 'question-detail') {
            return <QuestionDetail
                questionId={selectedQuestionId}
                onBack={handleBack}
            />;
        }

        if (view === 'year_select') {
            return <YearSelection onYearSelect={handleYearClick} />;
        }

        if (view === 'years') {
            return <PreviousYearPapers onQuestionSelect={(q) => {
                setSelectedQuestionId(q.question_id);
                setView('question-detail');
            }} />;
        }

        if (view === 'syllabus-subjects') {
            // Subject icons mapping for visual variety
            const subjectIcons = {
                'Aerospace Engineering': '🚀',
                'Mathematics': '📐',
                'General Aptitude': '🧠',
                'Flight Mechanics': '✈️',
                'Propulsion': '🔥',
                'Structures': '🏗️',
                'Aerodynamics': '💨',
                'default': '📚'
            };

            return (
                <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark scroll-smooth h-full">
                    <div className="max-w-[1200px] mx-auto p-8 space-y-8">
                        {/* Header Section */}
                        <div className="flex flex-col gap-2">
                            <h1 className="text-3xl font-bold text-slate-900 dark:text-white font-display">Browse by Syllabus</h1>
                            <p className="text-slate-500 dark:text-gray-400 text-lg">Master each subject area with topic-wise practice questions.</p>
                        </div>

                        {/* Subjects Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {Object.keys(syllabusTree).map((subject) => {
                                const topicCount = syllabusTree[subject]?.length || 0;
                                const icon = subjectIcons[subject] || subjectIcons['default'];

                                return (
                                    <button
                                        key={subject}
                                        onClick={() => handleSubjectClick(subject)}
                                        className="bg-white dark:bg-[#15192b] p-6 rounded-xl border border-slate-200 dark:border-border-dark 
                                                 hover:shadow-lg hover:border-primary/50 dark:hover:border-primary/50 
                                                 hover:-translate-y-0.5 cursor-pointer transition-all duration-200 group text-left"
                                    >
                                        <div className="flex flex-col gap-4">
                                            {/* Icon */}
                                            <div className="size-12 rounded-lg bg-primary/10 flex items-center justify-center text-2xl group-hover:bg-primary/20 transition-colors">
                                                {icon}
                                            </div>

                                            {/* Content */}
                                            <div>
                                                <h3 className="text-lg font-semibold text-slate-900 dark:text-white group-hover:text-primary transition-colors">
                                                    {subject}
                                                </h3>
                                                <p className="text-sm text-slate-500 dark:text-gray-400 mt-1">
                                                    {topicCount} {topicCount === 1 ? 'Topic' : 'Topics'} available
                                                </p>
                                            </div>

                                            {/* Action hint */}
                                            <div className="flex items-center gap-2 text-primary font-medium text-sm opacity-0 group-hover:opacity-100 transition-opacity">
                                                <span>Browse Questions</span>
                                                <span className="transform group-hover:translate-x-0.5 transition-transform">→</span>
                                            </div>
                                        </div>
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                </div>
            );
        }

        if (view === 'syllabus-topics') {
            return (
                <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark scroll-smooth h-full">
                    <div className="max-w-[1200px] mx-auto p-8 space-y-8">
                        {/* Header with Back Button */}
                        <div className="flex flex-col gap-4">
                            <button
                                onClick={() => setView('syllabus-subjects')}
                                className="self-start flex items-center gap-2 text-slate-500 dark:text-gray-400 hover:text-primary transition-colors font-medium"
                            >
                                <span>←</span>
                                <span>Back to Subjects</span>
                            </button>
                            <div>
                                <h1 className="text-3xl font-bold text-slate-900 dark:text-white font-display">{selectedSubject}</h1>
                                <p className="text-slate-500 dark:text-gray-400 text-lg mt-1">
                                    Select a topic to practice {syllabusTree[selectedSubject]?.length || 0} available topics.
                                </p>
                            </div>
                        </div>

                        {/* Topics Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                            {syllabusTree[selectedSubject]?.map((topic, index) => (
                                <button
                                    key={topic}
                                    onClick={() => handleTopicClick(topic)}
                                    className="bg-white dark:bg-card-dark p-5 rounded-xl shadow-sm border border-[#f0f2f4] dark:border-border-dark 
                                             hover:shadow-lg hover:border-primary/40 dark:hover:border-primary/40
                                             hover:-translate-y-0.5 cursor-pointer transition-all duration-200 group text-left"
                                >
                                    <div className="flex items-start gap-3">
                                        {/* Number badge */}
                                        <div className="size-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center text-sm font-bold shrink-0">
                                            {index + 1}
                                        </div>

                                        <div className="flex-1 min-w-0">
                                            <h3 className="font-semibold text-slate-900 dark:text-white group-hover:text-primary transition-colors line-clamp-2">
                                                {topic}
                                            </h3>
                                            <p className="text-xs text-slate-500 dark:text-gray-400 mt-1 group-hover:text-primary/70 transition-colors">
                                                Practice questions →
                                            </p>
                                        </div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            );
        }


        return (
            <>
                {view === 'home' && (
                    user ? (
                        <Dashboard
                            onSearch={performSearch}
                            onNavigate={(tab) => handleTabChange(tab)}
                        />
                    ) : (
                        <div className="hero">
                            <h1>Master Aerospace Engineering</h1>
                            <p>Search previous year questions by concept, topic, or keyword.</p>
                            <SearchBox onSearch={performSearch} initialValue={query} />
                        </div>
                    )
                )}

                {view === 'results' && (
                    <>
                        <div style={{ marginBottom: '1.5rem' }}>
                            <SearchBox onSearch={performSearch} initialValue={query} />
                        </div>

                        <div className="status-message">
                            {loading && (
                                <div className="results-grid" style={{ marginTop: 0 }}>
                                    {[1, 2, 3].map(i => <SkeletonCard key={i} />)}
                                </div>
                            )}

                            {!loading && error && (
                                <div className="error-state">{error}</div>
                            )}

                            {!loading && query && results.length === 0 && !error && (
                                <div className="empty-state">No questions found for this search. Try a broader topic.</div>
                            )}

                            {!loading && results.length > 0 && (
                                <div className="result-count">Found {total} {total === 1 ? 'question' : 'questions'}</div>
                            )}
                        </div>

                        <div className="results-grid">
                            {results.map((q) => (
                                <QuestionCard
                                    key={q.id}
                                    question={q}
                                    onClick={() => {
                                        setSelectedQuestionId(q.question_id);
                                        setView('question-detail');
                                    }}
                                />
                            ))}
                        </div>
                    </>
                )}
            </>
        );
    };

    return (
        <div className={`${theme}`}>
            {view === 'landing' ? (
                <>
                    <LandingPage
                        currentTheme={theme}
                        toggleTheme={toggleTheme}
                        onStart={() => setView('home')}
                        onLogin={() => {
                            openLogin();
                        }}
                        onRegister={() => {
                            openRegister();
                        }}
                        user={user}
                        onLogout={logout}
                    />
                    <AuthModal />
                </>
            ) : (
                <div className={`min-h-screen bg-background-light dark:bg-background-dark flex transition-colors duration-300 font-sans`}>
                    {!isZenMode && <Sidebar activeTab={activeTab} onTabChange={handleTabChange} onLogoClick={() => setView('landing')} onClose={() => setIsZenMode(true)} />}

                    <div className={`flex-1 flex flex-col min-h-screen transition-all duration-300 ${!isZenMode && 'lg:ml-72'}`}>
                        <Header
                            toggleTheme={toggleTheme}
                            theme={theme}
                            variant={view === 'question-detail' ? 'detail' : 'default'}
                            onBack={handleBack}
                            onToggleSidebar={toggleZenMode}
                            breadcrumbs={getBreadcrumbs()}
                            showSearch={view !== 'home'}
                        />

                        <main className={`flex-1 overflow-hidden relative ${view === 'results' ? 'results-mode' : ''} ${view !== 'home' ? 'p-4 sm:p-6 lg:p-8' : ''}`}>
                            {renderMainContent()}
                        </main>
                    </div>
                    <AuthModal />
                </div>
            )}
        </div>
    );
}

export default MainContent;
