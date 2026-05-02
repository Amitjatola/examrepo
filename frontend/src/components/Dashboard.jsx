import React, { useState, useEffect } from 'react';
import { Search, Sparkles, BookOpen, Clock, Flame, History, ChevronRight, TrendingUp, Target, ListChecks, Wand2, RefreshCw, Gauge, Timer } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
const Dashboard = ({
    onSearch,
    onNavigate,
    onPracticeWeakTopic,
    onOpenRemediationPlaylist,
    onRunMockPaper,
    onOpenQuestion,
}) => {
    const { user, isPremium } = useAuth();
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
        topicPerformance: {},
        conceptPerformance: {},
        timeStudiedSeconds: 0,
        topicAvgTimeSeconds: {},
        attemptAccuracyPct: 0,
        readinessScore: 0,
        syllabusTopicCatalogTotal: 0,
        recentActivity: [],
    });

    const [remediationItems, setRemediationItems] = useState([]);
    const [savedBookmarks, setSavedBookmarks] = useState([]);
    const [timeTargetSeconds, setTimeTargetSeconds] = useState(() => {
        const raw = Number(localStorage.getItem('ag_time_target_seconds'));
        return Number.isFinite(raw) && raw > 0 ? raw : 150;
    });

    const [plannerTarget, setPlannerTarget] = useState(() => localStorage.getItem('ag_planner_target') || 'good');
    const [plannerDays, setPlannerDays] = useState(() => localStorage.getItem('ag_planner_days') || '30');
    const [plannerMode, setPlannerMode] = useState(() => localStorage.getItem('ag_planner_mode') || 'smart');

    useEffect(() => {
        localStorage.setItem('ag_planner_target', plannerTarget);
        localStorage.setItem('ag_planner_days', plannerDays);
        localStorage.setItem('ag_planner_mode', plannerMode);
    }, [plannerTarget, plannerDays, plannerMode]);

    useEffect(() => {
        localStorage.setItem('ag_time_target_seconds', String(timeTargetSeconds));
    }, [timeTargetSeconds]);

    useEffect(() => {
        if (!user) {
            setRemediationItems([]);
            setSavedBookmarks([]);
            return undefined;
        }
        let cancelled = false;
        (async () => {
            try {
                const [rem, marks] = await Promise.all([
                    api.get('/dashboard/remediation', { limit: 12 }),
                    api.get('/users/me/bookmarks', { limit: 8 }),
                ]);
                if (cancelled) return;
                setRemediationItems(rem.items || []);
                setSavedBookmarks(Array.isArray(marks) ? marks : []);
            } catch {
                if (!cancelled) {
                    setRemediationItems([]);
                    setSavedBookmarks([]);
                }
            }
        })();
        return () => {
            cancelled = true;
        };
    }, [user]);

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
                    topicPerformance: data.topic_performance || {},
                    conceptPerformance: data.concept_performance || {},
                    timeStudiedSeconds: data.time_studied_seconds ?? 0,
                    recentActivity: data.recent_activity || [],
                    topicAvgTimeSeconds: data.topic_avg_time_seconds || {},
                    attemptAccuracyPct: data.attempt_accuracy_pct ?? 0,
                    readinessScore: data.readiness_score ?? 0,
                    syllabusTopicCatalogTotal: data.syllabus_topic_catalog_total ?? 0,
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



    // Removed quote logic as per refactor plan
    
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
                                Syllabus coverage (topics touched / catalog): {stats.syllabusProgress}% · Catalog topics:{' '}
                                {stats.syllabusTopicCatalogTotal || '—'}
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

                    {/* Performance Ribbon */}
                    <div className="flex flex-col md:flex-row bg-white dark:bg-[#15192b] border border-slate-200 dark:border-border-dark rounded-xl divide-y md:divide-y-0 md:divide-x divide-slate-200 dark:divide-border-dark overflow-hidden shadow-sm">
                        {/* Stat 1: Questions Attempted (Link to History) */}
                        <button onClick={() => onNavigate('history')} className="flex-1 flex flex-col gap-1 p-5 hover:bg-slate-50 dark:hover:bg-white/5 transition-colors text-left group">
                            <div className="flex justify-between items-start mb-2">
                                <div className="p-2 rounded-lg bg-slate-100 dark:bg-[#2f396a]/50 text-slate-600 dark:text-white group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                                    <BookOpen size={20} />
                                </div>
                                <div className="flex items-center gap-1 text-green-600 bg-green-100 dark:bg-green-500/10 px-2 py-0.5 rounded text-xs font-medium">
                                    <TrendingUp size={12} />
                                    {loading ? '-' : `${stats.attemptAccuracyPct}% acc`}
                                </div>
                            </div>
                            <p className="text-slate-500 dark:text-text-muted text-sm font-medium">Questions Attempted</p>
                            <p className="text-[11px] text-slate-400 dark:text-slate-500 font-medium">
                                Bank coverage {loading ? '-' : `${stats.attemptPercentage}%`}
                            </p>
                            <div className="flex items-center justify-between mt-1">
                                <p className="text-slate-900 dark:text-white text-2xl font-bold">{loading ? '-' : stats.questionsAttempted.toLocaleString()}</p>
                                <ChevronRight size={16} className="text-slate-400 group-hover:text-primary transition-colors transform group-hover:translate-x-1" />
                            </div>
                        </button>

                        {/* Stat 2: Hours Studied */}
                        <div className="flex-1 flex flex-col gap-1 p-5">
                            <div className="flex justify-between items-start mb-2">
                                <div className="p-2 rounded-lg bg-slate-100 dark:bg-[#2f396a]/50 text-slate-600 dark:text-white">
                                    <Clock size={20} />
                                </div>
                            </div>
                            <p className="text-slate-500 dark:text-text-muted text-sm font-medium">Time Studied</p>
                            <p className="text-slate-900 dark:text-white text-2xl font-bold mt-1">
                                {loading ? '-' : formatStudyTime(stats.timeStudiedSeconds || stats.hoursStudied * 3600)}
                            </p>
                        </div>

                        {/* Stat 3: Current Streak */}
                        <div className="flex-1 flex flex-col gap-1 p-5">
                            <div className="flex justify-between items-start mb-2">
                                <div className="p-2 rounded-lg bg-slate-100 dark:bg-[#2f396a]/50 text-slate-600 dark:text-white">
                                    <Flame size={20} />
                                </div>
                            </div>
                            <p className="text-slate-500 dark:text-text-muted text-sm font-medium">Current Streak</p>
                            <p className="text-slate-900 dark:text-white text-2xl font-bold mt-1">{stats.currentStreak} Days</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        <div className="rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] p-6 flex flex-col gap-3">
                            <div className="flex items-center gap-2">
                                <Gauge size={18} className="text-primary" />
                                <h3 className="text-slate-900 dark:text-white font-semibold">Readiness lite</h3>
                            </div>
                            <p className="text-xs text-slate-500 dark:text-text-muted leading-relaxed">
                                Honest score = attempt accuracy × syllabus coverage ÷ 100. No rank prediction.
                                <span className="block mt-1 font-mono text-[11px] text-slate-400 dark:text-slate-500">
                                    readiness = {loading ? '…' : `${stats.attemptAccuracyPct}% × ${stats.syllabusProgress}% ÷ 100`}{' '}
                                    → <span className="text-primary font-bold">{loading ? '…' : `${stats.readinessScore}%`}</span>
                                </span>
                            </p>
                            <div className="text-4xl font-black text-slate-900 dark:text-white">{loading ? '-' : `${stats.readinessScore}%`}</div>
                        </div>

                        <div className="rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] p-6 flex flex-col gap-4">
                            <div className="flex flex-wrap justify-between gap-3 items-center">
                                <div className="flex items-center gap-2">
                                    <Timer size={18} className="text-primary" />
                                    <h3 className="text-slate-900 dark:text-white font-semibold">Time insights</h3>
                                </div>
                                <label className="flex flex-col text-[11px] font-semibold text-slate-500 gap-1">
                                    Target (sec/Q)
                                    <input
                                        type="number"
                                        min={30}
                                        max={600}
                                        value={timeTargetSeconds}
                                        onChange={(e) => setTimeTargetSeconds(Number(e.target.value) || 150)}
                                        className="w-28 rounded-lg border border-slate-200 dark:border-border-dark bg-white dark:bg-[#1a1d2e] text-sm px-2 py-1 text-slate-900 dark:text-white"
                                    />
                                </label>
                            </div>
                            <p className="text-xs text-slate-500 dark:text-text-muted">
                                Avg seconds per attempt by topic vs your target; flagged topics need pacing drills.
                            </p>
                            <div className="flex flex-col gap-2 max-h-52 overflow-y-auto">
                                {Object.keys(stats.topicAvgTimeSeconds || {}).length === 0 && (
                                    <p className="text-sm text-slate-400 italic">Attempt questions to populate timing.</p>
                                )}
                                {Object.entries(stats.topicAvgTimeSeconds || {})
                                    .sort(([, a], [, b]) => b - a)
                                    .slice(0, 10)
                                    .map(([topic, avg]) => {
                                        const slow = avg > timeTargetSeconds;
                                        return (
                                            <div
                                                key={topic}
                                                className={`flex justify-between gap-3 text-sm px-3 py-2 rounded-lg border ${
                                                    slow
                                                        ? 'border-orange-200 dark:border-orange-900/40 bg-orange-50/60 dark:bg-orange-950/20'
                                                        : 'border-slate-100 dark:border-white/5 bg-slate-50 dark:bg-white/5'
                                                }`}
                                            >
                                                <span className="truncate text-slate-800 dark:text-slate-100">{topic}</span>
                                                <span className="shrink-0 font-bold text-slate-700 dark:text-slate-200">
                                                    {avg}s {slow ? '(slow)' : ''}
                                                </span>
                                            </div>
                                        );
                                    })}
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        <div className="rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] p-6 flex flex-col gap-3">
                            <div className="flex justify-between items-center gap-3">
                                <h3 className="text-slate-900 dark:text-white font-semibold flex items-center gap-2">
                                    <RefreshCw size={18} className="text-amber-500" />
                                    Wrong-answer queue
                                </h3>
                                <button
                                    type="button"
                                    onClick={() => onOpenRemediationPlaylist?.()}
                                    className="text-xs font-bold text-primary hover:underline cursor-pointer"
                                >
                                    Play all
                                </button>
                            </div>
                            <p className="text-xs text-slate-500 dark:text-text-muted">Distinct misses (most recent first).</p>
                            <div className="flex flex-col gap-2 max-h-56 overflow-y-auto">
                                {remediationItems.length === 0 ? (
                                    <p className="text-sm text-slate-400 italic">No misses logged yet — keep practicing.</p>
                                ) : (
                                    remediationItems.map((item) => (
                                        <div
                                            key={item.question_id}
                                            className="flex justify-between gap-3 items-center px-3 py-2 rounded-lg border border-slate-100 dark:border-white/5 bg-slate-50 dark:bg-white/5"
                                        >
                                            <span className="text-sm font-medium text-slate-800 dark:text-slate-100 truncate">
                                                {item.question_id.replace(/_/g, ' ')}
                                            </span>
                                            <button
                                                type="button"
                                                onClick={() => onOpenQuestion?.(item.question_id)}
                                                className="text-xs font-bold text-primary hover:underline cursor-pointer shrink-0"
                                            >
                                                Open
                                            </button>
                                        </div>
                                    ))
                                )}
                            </div>
                            <button
                                type="button"
                                onClick={() => {
                                    const sorted = Object.entries(stats.topicPerformance || {}).sort((a, b) => a[1] - b[1]);
                                    if (sorted[0]) onPracticeWeakTopic?.(sorted[0][0]);
                                }}
                                className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 dark:border-border-dark px-4 py-2 text-sm font-semibold text-slate-800 dark:text-slate-100 hover:bg-slate-50 dark:hover:bg-white/5 cursor-pointer"
                            >
                                <Target size={16} />
                                Practice weakest topic
                            </button>
                        </div>

                        <div className="rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] p-6 flex flex-col gap-3">
                            <h3 className="text-slate-900 dark:text-white font-semibold flex items-center gap-2">
                                <BookOpen size={18} className="text-primary" />
                                Saved questions
                            </h3>
                            <p className="text-xs text-slate-500 dark:text-text-muted">Bookmarks + notes you saved.</p>
                            <div className="flex flex-col gap-2 max-h-56 overflow-y-auto">
                                {savedBookmarks.length === 0 ? (
                                    <p className="text-sm text-slate-400 italic">Bookmark questions from detail view.</p>
                                ) : (
                                    savedBookmarks.map((b) => (
                                        <button
                                            key={b.question_id}
                                            type="button"
                                            onClick={() => onOpenQuestion?.(b.question_id)}
                                            className="text-left px-3 py-2 rounded-lg border border-slate-100 dark:border-white/5 hover:border-primary/40 hover:bg-slate-50 dark:hover:bg-white/5 cursor-pointer"
                                        >
                                            <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
                                                {b.question_id.replace(/_/g, ' ')}
                                            </p>
                                            {b.note && (
                                                <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2">{b.note}</p>
                                            )}
                                        </button>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Main Content Split */}
                    <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
                        <div className="xl:col-span-2 flex flex-col gap-6">
                            <div className="rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] p-6 flex flex-col gap-4">
                                <div className="flex flex-wrap justify-between items-center gap-3">
                                    <h3 className="text-slate-900 dark:text-white font-semibold flex items-center gap-2">
                                        <ListChecks size={18} className="text-primary" />
                                        Study planner
                                    </h3>
                                    <span className="text-xs text-slate-500 dark:text-text-muted">
                                        {plannerMode === 'yield' ? 'Yield: weak topics + traps first' : 'Smart: balance weak areas + coverage'}
                                    </span>
                                </div>
                                <div className="flex flex-wrap gap-3">
                                    <label className="flex flex-col text-xs font-semibold text-slate-500 gap-1">
                                        Target band
                                        <select
                                            value={plannerTarget}
                                            onChange={(e) => setPlannerTarget(e.target.value)}
                                            className="rounded-lg border border-slate-200 dark:border-border-dark bg-white dark:bg-[#1a1d2e] text-sm text-slate-900 dark:text-white px-3 py-2"
                                        >
                                            <option value="qualifying">Qualifying</option>
                                            <option value="good">Comfortable pass</option>
                                            <option value="ranker">Ranker</option>
                                        </select>
                                    </label>
                                    <label className="flex flex-col text-xs font-semibold text-slate-500 gap-1">
                                        Time left
                                        <select
                                            value={plannerDays}
                                            onChange={(e) => setPlannerDays(e.target.value)}
                                            className="rounded-lg border border-slate-200 dark:border-border-dark bg-white dark:bg-[#1a1d2e] text-sm text-slate-900 dark:text-white px-3 py-2"
                                        >
                                            <option value="5">Crash (~5 days)</option>
                                            <option value="30">Month (~30 days)</option>
                                            <option value="60">Detailed (~60 days)</option>
                                        </select>
                                    </label>
                                    <div className="flex flex-col text-xs font-semibold text-slate-500 gap-1">
                                        Mode
                                        <div className="flex rounded-lg border border-slate-200 dark:border-border-dark overflow-hidden">
                                            <button
                                                type="button"
                                                onClick={() => setPlannerMode('smart')}
                                                className={`px-3 py-2 text-sm font-medium ${plannerMode === 'smart' ? 'bg-primary text-white' : 'bg-white dark:bg-[#1a1d2e] text-slate-700 dark:text-slate-200'}`}
                                            >
                                                Smart
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => setPlannerMode('yield')}
                                                className={`px-3 py-2 text-sm font-medium ${plannerMode === 'yield' ? 'bg-primary text-white' : 'bg-white dark:bg-[#1a1d2e] text-slate-700 dark:text-slate-200'}`}
                                            >
                                                Yield
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                <p className="text-xs text-slate-500 dark:text-text-muted">
                                    Next steps (tap to run). Weights adjust with your heatmap over time.
                                </p>
                                <div className="flex flex-col sm:flex-row flex-wrap gap-2">
                                    <button
                                        type="button"
                                        onClick={() => {
                                            const sorted = Object.entries(stats.topicPerformance || {}).sort(
                                                (a, b) => a[1] - b[1]
                                            );
                                            if (sorted[0]) onPracticeWeakTopic?.(sorted[0][0]);
                                        }}
                                        className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-4 py-2.5 text-sm font-semibold hover:opacity-90"
                                    >
                                        <Target size={16} />
                                        Weakest topic drill
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => {
                                            const sorted = Object.entries(stats.conceptPerformance || {}).sort(
                                                (a, b) => a[1] - b[1]
                                            );
                                            if (sorted[0]) onSearch(sorted[0][0]);
                                        }}
                                        className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 dark:border-border-dark px-4 py-2.5 text-sm font-semibold text-slate-800 dark:text-slate-100 hover:bg-slate-50 dark:hover:bg-white/5"
                                    >
                                        <Search size={16} />
                                        Weakest concept search
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => onOpenRemediationPlaylist?.()}
                                        className="inline-flex items-center justify-center gap-2 rounded-lg border border-amber-200 dark:border-amber-900/50 bg-amber-50/80 dark:bg-amber-950/30 px-4 py-2.5 text-sm font-semibold text-amber-950 dark:text-amber-100"
                                    >
                                        <RefreshCw size={16} />
                                        Fix mistakes
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => onRunMockPaper?.()}
                                        className="inline-flex items-center justify-center gap-2 rounded-lg border border-primary/40 bg-primary/10 px-4 py-2.5 text-sm font-semibold text-primary"
                                    >
                                        <Wand2 size={16} />
                                        Adaptive mock {isPremium ? '' : '(Pro)'}
                                    </button>
                                </div>
                            </div>

                            <div className="rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] p-6 flex flex-col gap-4">
                                <h3 className="text-slate-900 dark:text-white font-semibold">Concept mastery</h3>
                                <p className="text-xs text-slate-500 dark:text-text-muted">
                                    Accuracy by tagged concept (from your attempts). Tap a row to search.
                                </p>
                                <div className="flex flex-col gap-2 max-h-64 overflow-y-auto">
                                    {Object.keys(stats.conceptPerformance || {}).length > 0 ? (
                                        Object.entries(stats.conceptPerformance)
                                            .sort(([, a], [, b]) => a - b)
                                            .slice(0, 12)
                                            .map(([concept, accuracy]) => (
                                                <button
                                                    key={concept}
                                                    type="button"
                                                    onClick={() => onSearch(concept)}
                                                    className="flex justify-between items-center text-left text-sm py-2 px-3 rounded-lg border border-slate-100 dark:border-white/5 hover:border-primary/40 hover:bg-slate-50 dark:hover:bg-white/5"
                                                >
                                                    <span className="text-slate-800 dark:text-slate-100 truncate pr-2">
                                                        {concept}
                                                    </span>
                                                    <span className="font-bold text-slate-600 dark:text-slate-300 shrink-0">
                                                        {accuracy}%
                                                    </span>
                                                </button>
                                            ))
                                    ) : (
                                        <p className="text-sm text-slate-400 italic py-4 text-center">
                                            Concept stats appear after you practice questions with concept tags.
                                        </p>
                                    )}
                                </div>
                            </div>
                        </div>

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
                                                        <div className="flex justify-between items-center text-sm gap-2">
                                                            <span className="text-slate-700 dark:text-slate-200 font-medium truncate max-w-[50%]">{topic}</span>
                                                            <span className={`text-${color}-600 dark:text-${color}-400 font-bold shrink-0`}>{accuracy}%</span>
                                                        </div>
                                                        <div className="w-full bg-slate-100 dark:bg-[#2f396a] h-2 rounded-full overflow-hidden">
                                                            <div
                                                                className={`h-full rounded-full transition-all duration-500 bg-${color}-500`}
                                                                style={{ width: `${accuracy}%` }}
                                                            ></div>
                                                        </div>
                                                        {onPracticeWeakTopic && (
                                                            <button
                                                                type="button"
                                                                onClick={() => onPracticeWeakTopic(topic)}
                                                                className="self-start mt-1 inline-flex items-center gap-1 text-xs font-semibold text-primary hover:text-primary/80 transition-colors"
                                                            >
                                                                <Target size={12} />
                                                                Practice this topic
                                                            </button>
                                                        )}
                                                    </div>
                                                );
                                            })
                                    ) : (
                                        <div className="relative py-4">
                                            {/* Ghost Grid */}
                                            <div className="grid grid-cols-10 gap-1 opacity-20">
                                                {Array.from({ length: 50 }).map((_, i) => (
                                                    <div key={i} className="aspect-square bg-slate-400 dark:bg-slate-600 rounded-sm"></div>
                                                ))}
                                            </div>
                                            {/* Overlay */}
                                            <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/70 dark:bg-[#15192b]/70 backdrop-blur-[2px]">
                                                <p className="text-sm font-semibold text-slate-900 dark:text-white mb-2">No data recorded yet.</p>
                                                <button
                                                    onClick={() => onNavigate('year_select')}
                                                    className="px-4 py-1.5 bg-primary text-white text-sm font-medium rounded shadow-sm hover:bg-primary/90 transition-colors"
                                                >
                                                    Start Practicing
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Recent Activity */}
                            <div className="rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] p-6 flex flex-col gap-4">
                                <div className="flex justify-between items-center">
                                    <h3 className="text-slate-900 dark:text-white font-semibold flex items-center gap-2">
                                        <History size={18} className="text-slate-400" />
                                        Recent Activity
                                    </h3>
                                </div>
                                
                                <div className="flex flex-col gap-3 mt-1">
                                    {stats.recentActivity && stats.recentActivity.length > 0 ? (
                                        stats.recentActivity.map((attempt, index) => (
                                            <div key={index} className="flex items-start gap-3 p-3 rounded-lg border border-slate-100 dark:border-white/5 bg-slate-50 dark:bg-white/5">
                                                <div className={`mt-0.5 w-2 h-2 rounded-full shrink-0 ${attempt.is_correct ? 'bg-green-500' : 'bg-red-500'}`}></div>
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-sm font-medium text-slate-800 dark:text-slate-200 truncate">
                                                        {attempt.question_id.replace(/_/g, ' ')}
                                                    </p>
                                                    <p className="text-xs text-slate-500 dark:text-slate-400 truncate mt-0.5">
                                                        {attempt.question_text}
                                                    </p>
                                                </div>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="text-center py-6 text-slate-400 dark:text-text-muted text-sm italic">
                                            Complete questions to track your history.
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
