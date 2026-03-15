import React, { useState, useEffect, useCallback } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import SearchBox from './SearchBox';
import QuestionCard from './QuestionCard';
import SkeletonCard from './SkeletonCard';
import PaperAttemptView from './PaperAttemptView';
import QuestionDetail from './QuestionDetail';
import YearSelection from './YearSelection';
import LandingPage from './LandingPage';
import AuthModal from './AuthModal';
import Dashboard from './Dashboard';
import PremiumPage from './PremiumPage';
import SyllabusSelection from './SyllabusSelection';
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
    const [selectedYear, setSelectedYear] = useState(savedState?.selectedYear || null);
    const [selectedQuestionId, setSelectedQuestionId] = useState(savedState?.selectedQuestionId || null);

    const toggleZenMode = () => setIsZenMode(!isZenMode);
    const [results, setResults] = useState([]);
    const [error, setError] = useState(null);
    const [total, setTotal] = useState(0);

    // State for back button handling
    const isPopping = React.useRef(false);

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

        // Push to history stack if not popping
        if (!isPopping.current) {
            window.history.pushState(stateToSave, '', '');
        } else {
            // Reset the flag
            isPopping.current = false;
        }
    }, [view, activeTab, query, selectedSubject, selectedTopic, selectedQuestionId]);

    // Handle back button (popstate)
    useEffect(() => {
        const handlePopState = (event) => {
            if (event.state) {
                isPopping.current = true; // Prevent pushing this state back
                // Restore state from history
                const s = event.state;
                if (s.view) setView(s.view);
                if (s.activeTab) setActiveTab(s.activeTab);
                if (s.query !== undefined) setQuery(s.query); // checking undefined allows empty string
                if (s.selectedSubject !== undefined) setSelectedSubject(s.selectedSubject);
                if (s.selectedTopic !== undefined) setSelectedTopic(s.selectedTopic);
                if (s.selectedQuestionId !== undefined) setSelectedQuestionId(s.selectedQuestionId);
            }
        };

        window.addEventListener('popstate', handlePopState);

        // Initial replaceState to ensure we have a valid starting state
        const initialState = {
            view,
            activeTab,
            query,
            selectedSubject,
            selectedTopic,
            selectedQuestionId,
        };
        window.history.replaceState(initialState, '', '');

        return () => window.removeEventListener('popstate', handlePopState);
        // We only want to set up the listener once
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

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
        } else if (tabId === 'premium') {
            setView('premium');
        }
    };

    const handleYearClick = (year) => {
        setSelectedYear(year);
        setView('years');
    };

    const handleSubjectClick = (subject) => {
        setSelectedSubject(subject);
        setView('syllabus-topics');
    };

    const handleTopicClick = async (topic) => {
        setSelectedTopic(topic);
        setQuery(topic); // Optional: show topic name in search box

        setView('results');
        setLoading(true);
        setError(null);

        try {
            // Use exact topic filtering instead of text search
            const data = await api.get('/search', { topic: topic, q: '' });
            setResults(data.questions);
            setTotal(data.total);
        } catch (err) {
            setError(`Error: ${err.message}. Make sure the backend is running.`);
        } finally {
            setLoading(false);
        }
    };

    const handleBack = () => {
        if (view === 'question-detail') {
            // From Detail -> List
            if (activeTab === 'year_select') setView('results');
            else if (activeTab === 'concepts') setView('results');
            else setView('results');
        } else if (view === 'results') {
            // From List -> Category/Index
            if (activeTab === 'year_select') setView('year_select');
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
            return <PaperAttemptView
                year={selectedYear}
                onBack={() => setView('year_select')}
                onPremium={() => setView('pricing')}
            />;
        }

        if (view === 'syllabus-subjects') {
            return (
                <SyllabusSelection
                    syllabusTree={syllabusTree}
                    onSubjectSelect={handleSubjectClick}
                    onSearch={performSearch}
                    query={query}
                />
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

        if (view === 'premium') {
            return <PremiumPage />;
        }


        if (view === 'pricing') {
            return (
                <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark scroll-smooth h-full">
                    <div className="max-w-4xl mx-auto p-8 space-y-8 text-center">
                        <h1 className="text-4xl font-bold text-slate-900 dark:text-white font-display mb-4">Simple, Transparent Pricing</h1>
                        <p className="text-lg text-slate-600 dark:text-gray-400 mb-12">Start for free, upgrade for mastery.</p>

                        <div className="grid md:grid-cols-2 gap-8 text-left">
                            {/* Free Plan */}
                            <div className="p-8 rounded-2xl border border-slate-200 dark:border-border-dark bg-white dark:bg-card-dark relative">
                                <h3 className="text-xl font-bold text-slate-900 dark:text-white">Basic</h3>
                                <div className="mt-4 flex items-baseline text-slate-900 dark:text-white">
                                    <span className="text-4xl font-extrabold tracking-tight">Free</span>
                                </div>
                                <p className="mt-4 text-slate-500 dark:text-gray-400">Everything you need to start practicing.</p>
                                <ul className="mt-8 space-y-4">
                                    {['Access to ALL papers (2007–2024)', 'Full search & syllabus browsing', 'Community discussions', 'Basic answer checking'].map(feature => (
                                        <li key={feature} className="flex items-center">
                                            <span className="material-symbols-outlined text-green-500 mr-3 text-sm">check</span>
                                            <span className="text-slate-600 dark:text-gray-300">{feature}</span>
                                        </li>
                                    ))}
                                </ul>
                                <button onClick={() => setView('home')} className="mt-8 w-full block bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white font-bold py-3 rounded-xl hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">
                                    Current Plan
                                </button>
                            </div>

                            {/* Pro Plan */}
                            <div className="p-8 rounded-2xl border-2 border-primary bg-white dark:bg-card-dark relative shadow-2xl shadow-primary/10">
                                <div className="absolute top-0 right-0 -mr-1 -mt-1 bg-primary text-white text-xs font-bold px-3 py-1 rounded-bl-xl rounded-tr-lg">POPULAR</div>
                                <h3 className="text-xl font-bold text-slate-900 dark:text-white">Pro</h3>
                                <div className="mt-4 flex items-baseline text-slate-900 dark:text-white">
                                    <span className="text-4xl font-extrabold tracking-tight">$9</span>
                                    <span className="ml-1 text-xl font-semibold text-slate-500">/month</span>
                                </div>
                                <p className="mt-4 text-slate-500 dark:text-gray-400">For serious aspirants.</p>
                                <ul className="mt-8 space-y-4">
                                    {['Everything in Free, plus:', 'AI-powered deep-dive analytics', 'Step-by-step solution derivations', 'Topic classification & research insights', 'Priority support'].map(feature => (
                                        <li key={feature} className="flex items-center">
                                            <span className="material-symbols-outlined text-primary mr-3 text-sm">check_circle</span>
                                            <span className="text-slate-600 dark:text-gray-300 font-medium">{feature}</span>
                                        </li>
                                    ))}
                                </ul>
                                <button className="mt-8 w-full block bg-primary text-white font-bold py-3 rounded-xl hover:bg-primary/90 transition-colors shadow-lg shadow-primary/25">
                                    Upgrade Now
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            );
        }

        if (view === 'about') {
            return (
                <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark scroll-smooth h-full">
                    <div className="max-w-3xl mx-auto p-8 space-y-8">
                        <h1 className="text-4xl font-bold text-slate-900 dark:text-white font-display mb-2">About ExamPrep</h1>
                        <p className="text-xl text-slate-600 dark:text-gray-400 leading-relaxed">
                            We are building the world's most intelligent platform for competitive exam preparation.
                        </p>

                        <div className="prose dark:prose-invert max-w-none">
                            <p>
                                Traditional preparation involves sifting through PDF books and random websites. ExamPrep brings structure to the chaos by indexing thousands of questions by <strong>concept</strong>, not just year.
                            </p>
                            <p>
                                Our mission is to help you minimize time spent <em>searching</em> for questions and maximize time spent <em>solving</em> them.
                            </p>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mt-8">
                            <div className="p-6 bg-slate-50 dark:bg-card-dark rounded-xl border border-slate-200 dark:border-border-dark">
                                <h4 className="font-bold text-slate-900 dark:text-white mb-2">Data Driven</h4>
                                <p className="text-sm text-slate-500 dark:text-gray-400">Everything is tagged and analyzed to give you insights.</p>
                            </div>
                            <div className="p-6 bg-slate-50 dark:bg-card-dark rounded-xl border border-slate-200 dark:border-border-dark">
                                <h4 className="font-bold text-slate-900 dark:text-white mb-2">Community Focused</h4>
                                <p className="text-sm text-slate-500 dark:text-gray-400">Learn from peers in our dedicated discussion threads.</p>
                            </div>
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
                        <div className="flex flex-col items-center justify-center min-h-[70vh] px-4 text-center animate-in fade-in duration-500 pb-40">
                            {/* Decorative background elements */}
                            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-primary/5 blur-[120px] rounded-full pointer-events-none"></div>

                            <div className="relative z-10 max-w-2xl w-full">
                                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold mb-6">
                                    <span className="flex size-2 rounded-full bg-primary animate-pulse"></span>
                                    READY TO PRACTICE?
                                </div>

                                <h1 className="text-4xl md:text-5xl font-bold text-slate-900 dark:text-white font-display tracking-tight mb-4">
                                    Master Your Exam
                                </h1>
                                <p className="text-lg text-slate-600 dark:text-gray-400 mb-10 max-w-lg mx-auto">
                                    Search thousands of past questions by topic, concept, or keyword.
                                </p>

                                <div className="relative group">
                                    <div className="absolute -inset-1 bg-gradient-to-r from-primary to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
                                    <div className="relative">
                                        <SearchBox onSearch={performSearch} initialValue={query} />
                                    </div>
                                </div>

                                {/* Popular Topics / Exploration */}
                                <div className="mt-12">
                                    <p className="text-sm font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-4">Popular Topics</p>
                                    <div className="flex flex-wrap justify-center gap-2">
                                        {['Fluid Mechanics', 'Thermodynamics', 'Calculus', 'Linear Algebra', 'Propulsion'].map((topic) => (
                                            <button
                                                key={topic}
                                                onClick={() => {
                                                    setQuery(topic);
                                                    performSearch(topic);
                                                }}
                                                className="px-4 py-2 rounded-full bg-white dark:bg-card-dark border border-slate-200 dark:border-border-dark 
                                                         text-slate-600 dark:text-slate-300 text-sm font-medium hover:border-primary hover:text-primary 
                                                         dark:hover:border-primary dark:hover:text-primary transition-colors shadow-sm"
                                            >
                                                {topic}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>
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
                            variant={['question-detail', 'results'].includes(view) ? 'detail' : 'default'}
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
