import React, { useState, useEffect } from 'react';
import { Search, Sparkles, CornerDownLeft, BookOpen, Clock, Flame, Play, History, ChevronRight, Quote, TrendingUp } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';

const Dashboard = ({ onSearch, onNavigate }) => {
    const { user } = useAuth();
    const [searchQuery, setSearchQuery] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);

    // Fetch suggestions with debounce
    useEffect(() => {
        const fetchSuggestions = async () => {
            if (searchQuery.length < 2) {
                setSuggestions([]);
                return;
            }
            try {
                const results = await api.getSuggestions(searchQuery, 5);
                setSuggestions(results);
                setShowSuggestions(true);
            } catch (error) {
                console.error("Suggestion fetch error:", error);
            }
        };

        const timeoutId = setTimeout(fetchSuggestions, 300);
        return () => clearTimeout(timeoutId);
    }, [searchQuery]);

    const handleSearchSubmit = (e) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            onSearch(searchQuery);
            setShowSuggestions(false);
        }
    };

    const selectSuggestion = (suggestion) => {
        setSearchQuery(suggestion);
        onSearch(suggestion);
        setShowSuggestions(false);
    };

    const userName = user?.full_name || user?.email?.split('@')[0] || 'Student';



    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        questionsAttempted: 0,
        hoursStudied: 0,
        currentStreak: 0,
        syllabusProgress: 0,
        attemptPercentage: 0,
        topicPerformance: {}
    });

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await api.get('/dashboard/stats');
                setStats(prev => ({
                    ...prev,
                    questionsAttempted: data.questions_attempted,
                    attemptPercentage: data.attempt_percentage,
                    hoursStudied: data.hours_studied,
                    currentStreak: data.current_streak,
                    syllabusProgress: data.syllabus_progress,
                    topicPerformance: data.topic_performance
                }));
            } catch (error) {
                console.error("Failed to fetch dashboard stats:", error);
            } finally {
                setLoading(false);
            }
        };

        if (user) {
            fetchStats();
        }
    }, [user]);



    // Quote logic
    const [quote, setQuote] = useState({
        text: "Success is the sum of small efforts, repeated day in and day out.",
        author: "Robert Collier"
    });

    useEffect(() => {
        const fetchQuote = async () => {
            try {
                // Try Quotable API first for specific motivational/success quotes
                const res = await fetch('https://api.quotable.io/random?tags=motivational,success');
                // Check if response is OK
                if (!res.ok) throw new Error("Quotable API Failed");

                const data = await res.json();
                if (data && data.content) {
                    setQuote({
                        text: data.content,
                        author: data.author
                    });
                }
            } catch (err) {
                console.log("Primary API failed, falling back to local exam quotes.", err);
                // Fallback to local high-quality exam/success quotes if API fails
                const backupQuotes = [
                    { text: "The future belongs to those who believe in the beauty of their dreams.", author: "Eleanor Roosevelt" },
                    { text: "Don't watch the clock; do what it does. Keep going.", author: "Sam Levenson" },
                    { text: "Believe you can and you're halfway there.", author: "Theodore Roosevelt" },
                    { text: "The secret of success is to do the common thing uncommonly well.", author: "John D. Rockefeller Jr." },
                    { text: "Success doesn't come to you, you've got to go to it.", author: "Marva Collins" }
                ];
                const randomBackup = backupQuotes[Math.floor(Math.random() * backupQuotes.length)];
                setQuote(randomBackup);
            }
        };

        fetchQuote();
    }, []);

    const formatStudyTime = (seconds) => {
        if (!seconds) return '0h';
        if (seconds < 60) return '< 1m';
        if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
        return `${(seconds / 3600).toFixed(1)}h`;
    };

    return (
        <div className="flex-1 flex flex-col h-full overflow-hidden">
            {/* ... (Sticky Top Header - Unchanged) ... */}
            {/* Same header code as before, simplified in this view for brevity context matching */}
            <div className="sticky top-0 z-20 w-full bg-white/80 dark:bg-[#0f1323]/80 backdrop-blur-md border-b border-slate-200 dark:border-border-dark px-6 py-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="flex flex-col">
                    <h2 className="text-slate-900 dark:text-white text-xl font-bold leading-tight tracking-tight">Dashboard</h2>
                    <p className="text-slate-500 dark:text-text-muted text-sm hidden md:block">Track your progress and continue learning</p>
                </div>

                {/* Smart Search Box */}
                <div className="w-full md:w-[480px] relative">
                    <form onSubmit={handleSearchSubmit}>
                        <div className="relative flex items-center w-full group">
                            <div className="absolute left-3 text-slate-400 dark:text-text-muted transition-colors group-focus-within:text-primary">
                                <Search size={20} />
                            </div>
                            <input
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onFocus={() => searchQuery.length >= 2 && setShowSuggestions(true)}
                                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                                className="w-full bg-slate-100 dark:bg-[#1a1d2e] border border-slate-200 dark:border-border-dark hover:border-slate-300 dark:hover:border-border-dark/80 focus:border-primary rounded-lg py-2.5 pl-10 pr-12 text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-text-muted focus:ring-1 focus:ring-primary focus:outline-none transition-all"
                                placeholder="Search questions by concept, topic, or keyword..."
                            />
                            <div className="absolute right-3 flex items-center gap-1">
                                <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-medium text-slate-400 dark:text-text-muted bg-slate-200 dark:bg-[#2f396a] rounded border border-slate-300 dark:border-white/5">⌘K</kbd>
                            </div>
                        </div>
                    </form>

                    {/* Suggestions Dropdown */}
                    {showSuggestions && suggestions.length > 0 && (
                        <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-[#1a1d2e] border border-slate-200 dark:border-border-dark rounded-lg shadow-xl z-50 overflow-hidden">
                            {suggestions.map((suggestion, index) => (
                                <button
                                    key={index}
                                    onClick={() => selectSuggestion(suggestion)}
                                    className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-slate-50 dark:hover:bg-[#2f396a]/50 transition-colors"
                                >
                                    <Sparkles size={14} className="text-primary" />
                                    <span className="text-sm text-slate-700 dark:text-white">{suggestion}</span>
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto p-6 md:p-8">
                <div className="max-w-[1400px] mx-auto w-full flex flex-col gap-8">

                    {/* Welcome Section */}
                    <div className="flex flex-wrap justify-between items-end gap-4">
                        <div className="flex flex-col gap-1">
                            <p className="text-slate-900 dark:text-white text-3xl md:text-4xl font-black leading-tight tracking-tight">
                                Welcome back, {userName}
                            </p>
                            <p className="text-slate-500 dark:text-text-muted text-base">
                                You've completed {stats.syllabusProgress}% of your syllabus. Keep it up!
                            </p>
                        </div>
                        <div className="flex gap-3">

                            <button
                                onClick={() => onNavigate('year_select')}
                                className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-lg shadow-primary/20"
                            >
                                <Flame size={18} />
                                Quick Practice
                            </button>
                        </div>
                    </div>

                    {/* Top Stats Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {/* Stat 1: Questions Attempted */}
                        <div className="flex flex-col justify-between gap-2 rounded-xl p-5 border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] hover:border-primary/30 transition-colors">
                            <div className="flex justify-between items-start">
                                <div className="p-2 rounded-lg bg-slate-100 dark:bg-[#2f396a]/50 text-slate-600 dark:text-white">
                                    <BookOpen size={20} />
                                </div>
                                <div className="flex items-center gap-1 text-green-600 bg-green-100 dark:bg-green-500/10 px-2 py-0.5 rounded text-xs font-medium">
                                    <TrendingUp size={12} />
                                    {stats.attemptPercentage}%
                                </div>
                            </div>
                            <div>
                                <p className="text-slate-500 dark:text-text-muted text-sm font-medium">Questions Attempted</p>
                                <p className="text-slate-900 dark:text-white text-2xl font-bold mt-1">{loading ? '-' : stats.questionsAttempted.toLocaleString()}</p>
                            </div>
                        </div>

                        {/* Stat 2: Hours Studied */}
                        <div className="flex flex-col justify-between gap-2 rounded-xl p-5 border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] hover:border-primary/30 transition-colors">
                            <div className="flex justify-between items-start">
                                <div className="p-2 rounded-lg bg-slate-100 dark:bg-[#2f396a]/50 text-slate-600 dark:text-white">
                                    <Clock size={20} />
                                </div>
                            </div>
                            <div>
                                <p className="text-slate-500 dark:text-text-muted text-sm font-medium">Time Studied</p>
                                <p className="text-slate-900 dark:text-white text-2xl font-bold mt-1">
                                    {loading ? '-' : formatStudyTime(stats.timeStudiedSeconds || stats.hoursStudied * 3600)}
                                </p>
                            </div>
                        </div>

                        {/* Stat 3: Current Streak */}
                        <div className="flex flex-col justify-between gap-2 rounded-xl p-5 border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] hover:border-primary/30 transition-colors">
                            <div className="flex justify-between items-start">
                                <div className="p-2 rounded-lg bg-slate-100 dark:bg-[#2f396a]/50 text-slate-600 dark:text-white">
                                    <Flame size={20} />
                                </div>
                            </div>
                            <div>
                                <p className="text-slate-500 dark:text-text-muted text-sm font-medium">Current Streak</p>
                                <p className="text-slate-900 dark:text-white text-2xl font-bold mt-1">{stats.currentStreak} Days</p>
                            </div>
                        </div>


                    </div>

                    {/* Main Content Split */}
                    <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">


                        {/* RIGHT COLUMN */}
                        <div className="flex flex-col gap-6">
                            {/* Topic Heatmap (Visual Weak Areas) */}
                            <div className="rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] p-6 flex flex-col gap-4">
                                <div className="flex justify-between items-center">
                                    <h3 className="text-slate-900 dark:text-white font-semibold">Topic Heatmap</h3>
                                </div>
                                <p className="text-xs text-slate-500 dark:text-text-muted">Identify your weak areas instantly.</p>

                                <div className="flex flex-col gap-4 mt-2">
                                    {Object.keys(stats.topicPerformance).length > 0 ? (
                                        Object.entries(stats.topicPerformance)
                                            .sort(([, a], [, b]) => a - b) // Sort by lowest accuracy first (weakest areas)
                                            .slice(0, 5) // Show top 5 weakest/strongest
                                            .map(([topic, accuracy], i) => {
                                                let color = 'green';
                                                if (accuracy < 50) color = 'red';
                                                else if (accuracy < 80) color = 'yellow';

                                                return (
                                                    <div key={topic} className="flex flex-col gap-1.5">
                                                        <div className="flex justify-between items-center text-sm">
                                                            <span className="text-slate-700 dark:text-slate-200 font-medium truncate max-w-[70%]">{topic}</span>
                                                            <span className={`text-${color}-600 dark:text-${color}-400 font-bold`}>{accuracy}%</span>
                                                        </div>
                                                        <div className="w-full bg-slate-100 dark:bg-[#2f396a] h-2 rounded-full overflow-hidden">
                                                            <div
                                                                className={`h-full rounded-full transition-all duration-500 bg-${color}-500`}
                                                                style={{ width: `${accuracy}%` }}
                                                            ></div>
                                                        </div>
                                                    </div>
                                                );
                                            })
                                    ) : (
                                        <div className="py-8 text-center text-slate-400 dark:text-text-muted text-sm italic">
                                            No practice data yet. Solve questions to see your heatmap!
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Motivational Quote */}
                            <div className="rounded-xl p-6 bg-gradient-to-br from-primary/10 to-slate-50 dark:from-primary/20 dark:to-[#15192b] border border-primary/20 relative overflow-hidden">
                                <div className="relative z-10 flex flex-col gap-2">
                                    <Quote size={24} className="text-primary mb-2" />
                                    <p className="text-slate-800 dark:text-white font-medium text-lg leading-snug">"{quote.text}"</p>
                                    <p className="text-slate-500 dark:text-text-muted text-sm mt-2">— {quote.author}</p>
                                </div>
                                <div className="absolute -right-6 -bottom-6 size-32 bg-primary/20 rounded-full blur-3xl"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
