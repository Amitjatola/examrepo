import React, { useState, useEffect } from 'react';
import { Search, Sparkles, CornerDownLeft, BookOpen, Clock, Flame, PieChart, Play, History, ChevronRight, Quote, TrendingUp } from 'lucide-react';
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

    // Mock data for dashboard - in production, this would come from API
    const stats = {
        questionsAttempted: 1248,
        hoursStudied: 42.5,
        currentStreak: 5,
        syllabusProgress: 45,
    };

    const continueStudying = [
        { id: 1, subject: 'Aerodynamics', topic: 'Boundary Layers', progress: 75, color: 'orange' },
        { id: 2, subject: 'Flight Mechanics', topic: 'Stability & Control', progress: 32, color: 'blue' },
    ];

    const recentActivity = [
        { id: 1, topic: 'Thermodynamics Quiz', type: 'Practice', date: 'Today, 10:30 AM', status: 'In Progress', statusColor: 'yellow' },
        { id: 2, topic: 'Matrix Operations', type: 'Study', date: 'Yesterday', status: '85% Accuracy', statusColor: 'green' },
        { id: 3, topic: 'Propulsion Basics', type: 'Practice', date: 'Oct 24, 2024', status: 'Completed', statusColor: 'gray' },
    ];

    const focusAreas = [
        { topic: 'Compressible Flow', subject: 'Aerodynamics', accuracy: 45, color: 'red' },
        { topic: 'Laplace Transforms', subject: 'Mathematics', accuracy: 62, color: 'yellow' },
    ];

    return (
        <div className="flex-1 flex flex-col h-full overflow-hidden">
            {/* Sticky Top Header with Search */}
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
                                onClick={() => onNavigate('concepts')}
                                className="flex items-center gap-2 bg-slate-200 dark:bg-[#2f396a] hover:bg-slate-300 dark:hover:bg-[#38437a] text-slate-700 dark:text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-slate-300 dark:border-white/5"
                            >
                                <BookOpen size={18} />
                                Study Plan
                            </button>
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
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {/* Stat 1: Questions Attempted */}
                        <div className="flex flex-col justify-between gap-2 rounded-xl p-5 border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] hover:border-primary/30 transition-colors">
                            <div className="flex justify-between items-start">
                                <div className="p-2 rounded-lg bg-slate-100 dark:bg-[#2f396a]/50 text-slate-600 dark:text-white">
                                    <BookOpen size={20} />
                                </div>
                                <div className="flex items-center gap-1 text-green-600 bg-green-100 dark:bg-green-500/10 px-2 py-0.5 rounded text-xs font-medium">
                                    <TrendingUp size={12} />
                                    12%
                                </div>
                            </div>
                            <div>
                                <p className="text-slate-500 dark:text-text-muted text-sm font-medium">Questions Attempted</p>
                                <p className="text-slate-900 dark:text-white text-2xl font-bold mt-1">{stats.questionsAttempted.toLocaleString()}</p>
                            </div>
                        </div>

                        {/* Stat 2: Hours Studied */}
                        <div className="flex flex-col justify-between gap-2 rounded-xl p-5 border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] hover:border-primary/30 transition-colors">
                            <div className="flex justify-between items-start">
                                <div className="p-2 rounded-lg bg-slate-100 dark:bg-[#2f396a]/50 text-slate-600 dark:text-white">
                                    <Clock size={20} />
                                </div>
                                <div className="flex items-center gap-1 text-green-600 bg-green-100 dark:bg-green-500/10 px-2 py-0.5 rounded text-xs font-medium">
                                    +3.5h
                                </div>
                            </div>
                            <div>
                                <p className="text-slate-500 dark:text-text-muted text-sm font-medium">Hours Studied</p>
                                <p className="text-slate-900 dark:text-white text-2xl font-bold mt-1">{stats.hoursStudied}</p>
                            </div>
                        </div>

                        {/* Stat 3: Current Streak */}
                        <div className="flex flex-col justify-between gap-2 rounded-xl p-5 border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] hover:border-primary/30 transition-colors">
                            <div className="flex justify-between items-start">
                                <div className="p-2 rounded-lg bg-slate-100 dark:bg-[#2f396a]/50 text-slate-600 dark:text-white">
                                    <Flame size={20} />
                                </div>
                                <div className="flex items-center gap-1 text-green-600 bg-green-100 dark:bg-green-500/10 px-2 py-0.5 rounded text-xs font-medium">
                                    +1 Day
                                </div>
                            </div>
                            <div>
                                <p className="text-slate-500 dark:text-text-muted text-sm font-medium">Current Streak</p>
                                <p className="text-slate-900 dark:text-white text-2xl font-bold mt-1">{stats.currentStreak} Days</p>
                            </div>
                        </div>

                        {/* Stat 4: Syllabus Progress */}
                        <div className="flex flex-col justify-between gap-3 rounded-xl p-5 border border-slate-200 dark:border-border-dark bg-gradient-to-br from-white to-slate-50 dark:from-[#15192b] dark:to-[#1e233b] hover:border-primary/30 transition-colors relative overflow-hidden">
                            <div className="absolute top-0 right-0 p-3 opacity-10">
                                <PieChart size={48} />
                            </div>
                            <div>
                                <p className="text-slate-500 dark:text-text-muted text-sm font-medium">Total Syllabus</p>
                                <div className="flex items-end gap-2 mt-1">
                                    <p className="text-slate-900 dark:text-white text-2xl font-bold">{stats.syllabusProgress}%</p>
                                    <p className="text-slate-400 dark:text-text-muted text-xs mb-1.5">Completed</p>
                                </div>
                            </div>
                            <div className="w-full bg-slate-200 dark:bg-[#2f396a] rounded-full h-2 mt-1">
                                <div className="bg-primary h-2 rounded-full transition-all" style={{ width: `${stats.syllabusProgress}%` }}></div>
                            </div>
                            <p className="text-slate-400 dark:text-text-muted text-xs">On track for completion</p>
                        </div>
                    </div>

                    {/* Main Content Split */}
                    <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
                        {/* LEFT COLUMN */}
                        <div className="xl:col-span-2 flex flex-col gap-8">
                            {/* Continue Studying Section */}
                            <div className="flex flex-col gap-4">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                                        <Play size={20} className="text-primary" />
                                        Continue Studying
                                    </h3>
                                    <button onClick={() => onNavigate('concepts')} className="text-sm text-primary hover:text-primary/80 transition-colors">View All</button>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {continueStudying.map((item) => (
                                        <div key={item.id} className="flex flex-col gap-4 p-5 rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] hover:bg-slate-50 dark:hover:bg-[#1a1d2e] transition-all cursor-pointer group">
                                            <div className="flex gap-4">
                                                <div className={`size-12 rounded-lg bg-${item.color}-100 dark:bg-${item.color}-500/10 flex items-center justify-center text-${item.color}-500`}>
                                                    <BookOpen size={24} />
                                                </div>
                                                <div>
                                                    <h4 className="text-slate-900 dark:text-white font-medium text-lg group-hover:text-primary transition-colors">{item.subject}</h4>
                                                    <p className="text-slate-500 dark:text-text-muted text-sm">{item.topic}</p>
                                                </div>
                                            </div>
                                            <div className="flex flex-col gap-2 mt-2">
                                                <div className="flex justify-between text-xs font-medium">
                                                    <span className="text-slate-500 dark:text-text-muted">Progress</span>
                                                    <span className="text-slate-900 dark:text-white">{item.progress}%</span>
                                                </div>
                                                <div className="w-full bg-slate-200 dark:bg-[#2f396a] h-1.5 rounded-full">
                                                    <div className={`bg-${item.color}-500 h-1.5 rounded-full`} style={{ width: `${item.progress}%` }}></div>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Recent Activity */}
                            <div className="flex flex-col gap-4">
                                <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                                    <History size={20} className="text-primary" />
                                    Recent Activity
                                </h3>
                                <div className="bg-white dark:bg-[#15192b] border border-slate-200 dark:border-border-dark rounded-xl overflow-hidden">
                                    <table className="w-full text-left text-sm">
                                        <thead className="bg-slate-50 dark:bg-[#101323] border-b border-slate-200 dark:border-border-dark text-slate-500 dark:text-text-muted">
                                            <tr>
                                                <th className="px-6 py-3 font-medium">Topic</th>
                                                <th className="px-6 py-3 font-medium hidden md:table-cell">Type</th>
                                                <th className="px-6 py-3 font-medium hidden md:table-cell">Date</th>
                                                <th className="px-6 py-3 font-medium text-right">Status</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-200 dark:divide-border-dark">
                                            {recentActivity.map((activity) => (
                                                <tr key={activity.id} className="hover:bg-slate-50 dark:hover:bg-[#1a1d2e] transition-colors">
                                                    <td className="px-6 py-4 text-slate-900 dark:text-white font-medium">{activity.topic}</td>
                                                    <td className="px-6 py-4 text-slate-500 dark:text-text-muted hidden md:table-cell">{activity.type}</td>
                                                    <td className="px-6 py-4 text-slate-500 dark:text-text-muted hidden md:table-cell">{activity.date}</td>
                                                    <td className="px-6 py-4 text-right">
                                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${activity.statusColor}-100 dark:bg-${activity.statusColor}-500/10 text-${activity.statusColor}-600 dark:text-${activity.statusColor}-500`}>
                                                            {activity.status}
                                                        </span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>

                        {/* RIGHT COLUMN */}
                        <div className="flex flex-col gap-6">
                            {/* Performance Insights */}
                            <div className="rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-[#15192b] p-6 flex flex-col gap-4">
                                <div className="flex justify-between items-center">
                                    <h3 className="text-slate-900 dark:text-white font-semibold">Performance Insights</h3>
                                </div>
                                <div className="flex flex-col gap-6 mt-2">
                                    {/* Accuracy Chart Placeholder */}
                                    <div className="flex flex-col gap-2">
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="text-slate-500 dark:text-text-muted">Overall Accuracy</span>
                                            <span className="text-slate-900 dark:text-white font-bold">78%</span>
                                        </div>
                                        <div className="flex h-24 items-end gap-1 pb-2 border-b border-slate-200 dark:border-border-dark">
                                            {[40, 60, 50, 80, 78].map((height, i) => (
                                                <div
                                                    key={i}
                                                    className={`w-full rounded-t-sm transition-all hover:bg-primary ${i === 4 ? 'bg-primary' : 'bg-slate-200 dark:bg-[#2f396a]'}`}
                                                    style={{ height: `${height}%` }}
                                                ></div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Focus Areas */}
                                    <div className="flex flex-col gap-3">
                                        <p className="text-xs font-semibold text-slate-500 dark:text-text-muted uppercase tracking-wider">Focus Areas</p>
                                        {focusAreas.map((area, i) => (
                                            <div key={i} className={`flex items-center gap-3 p-3 rounded-lg bg-slate-50 dark:bg-[#1a1d2e] border border-slate-200 dark:border-border-dark border-l-4 border-l-${area.color}-500`}>
                                                <div className="flex-1">
                                                    <p className="text-slate-900 dark:text-white text-sm font-medium">{area.topic}</p>
                                                    <p className="text-slate-500 dark:text-text-muted text-xs">{area.subject} • {area.accuracy}% Accuracy</p>
                                                </div>
                                                <button className="text-slate-400 dark:text-text-muted hover:text-primary">
                                                    <ChevronRight size={20} />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Motivational Quote */}
                            <div className="rounded-xl p-6 bg-gradient-to-br from-primary/10 to-slate-50 dark:from-primary/20 dark:to-[#15192b] border border-primary/20 relative overflow-hidden">
                                <div className="relative z-10 flex flex-col gap-2">
                                    <Quote size={24} className="text-primary mb-2" />
                                    <p className="text-slate-800 dark:text-white font-medium text-lg leading-snug">"Success is the sum of small efforts, repeated day in and day out."</p>
                                    <p className="text-slate-500 dark:text-text-muted text-sm mt-2">— Robert Collier</p>
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
