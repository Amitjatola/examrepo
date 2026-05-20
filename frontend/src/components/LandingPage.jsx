import { useState, useEffect } from 'react'
import { Moon, Sun, LogOut, User, ArrowRight } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import ParticleNetwork from './ParticleNetwork'

const FLOATING_BADGES = [
    { label: 'Fluid Mechanics', color: '#06b6d4', top: '18%', right: '28%' },
    { label: 'Thermodynamics', color: '#8b5cf6', top: '25%', right: '8%' },
    { label: 'Aerospace Structures', color: '#10b981', top: '45%', right: '2%' },
    { label: 'Control Systems', color: '#3b82f6', top: '60%', right: '10%' },
    { label: 'Engineering Mathematics', color: '#f59e0b', top: '75%', right: '25%' },
]

const CYCLING_SUBTITLES = [
    'Concept-indexed question bank from 2007–2025',
    'AI-powered solutions with step-by-step hints',
    'GATE CBT simulator with virtual calculator',
    'Spaced revision that never lets you forget',
]

const FEATURES = [
    {
        icon: 'quiz',
        title: 'GATE CBT Simulator',
        desc: 'Authentic exam interface with palette, timer, and virtual scientific calculator. Practice like D-day.',
        metric: '2007–2025',
    },
    {
        icon: 'hub',
        title: 'Concept-Indexed Bank',
        desc: 'Every question tagged by subject, topic, and concept. Drill your weakest links with surgical precision.',
        metric: '12,480+ Qs',
    },
    {
        icon: 'psychology',
        title: 'AI Solutions & Hints',
        desc: 'Step-by-step explanations, progressive hints, common traps, and exam strategy per question.',
        metric: '11 Research Tabs',
    },
    {
        icon: 'bug_report',
        title: 'Mistake Museum',
        desc: 'All wrong answers tracked with error-type tagging. Gap drills auto-generated from prerequisites.',
        metric: 'Auto Gap Drills',
    },
    {
        icon: 'event_repeat',
        title: 'Spaced Revision (SM-2)',
        desc: 'Scientifically-spaced review queue. Never forget what you solved. Formula cheat sheet included.',
        metric: 'Smart Intervals',
    },
    {
        icon: 'speed',
        title: 'Readiness Score & Planner',
        desc: 'Live readiness estimation, topic heatmap, weekly focus plan, and days-to-target tracking.',
        metric: 'Live Analytics',
    },
]

const HOW_IT_WORKS = [
    { step: '01', title: 'Select Target Rank', desc: 'Set your AIR goal — the system calibrates difficulty and pacing to match.' },
    { step: '02', title: 'AI Detects Weak Concepts', desc: 'Knowledge graph maps your gaps in real-time from every attempt you make.' },
    { step: '03', title: 'Adaptive Practice Engine', desc: 'Personalized question sequences built daily. No random solving, just precision.' },
]

const CONCEPTS = [
    { icon: 'air', label: 'Aerodynamics', id: 'AE-01', questions: 1240, mastery: 87, difficulty: 'Hard' },
    { icon: 'flight', label: 'Flight Mechanics', id: 'AE-02', questions: 980, mastery: 72, difficulty: 'Medium' },
    { icon: 'rocket_launch', label: 'Propulsion', id: 'AE-03', questions: 1100, mastery: 65, difficulty: 'Hard' },
    { icon: 'construction', label: 'Structures', id: 'AE-04', questions: 1350, mastery: 80, difficulty: 'Hard' },
    { icon: 'satellite_alt', label: 'Space Dynamics', id: 'AE-05', questions: 720, mastery: 58, difficulty: 'Medium' },
    { icon: 'water_drop', label: 'Fluid Mechanics', id: 'AE-06', questions: 1500, mastery: 91, difficulty: 'Hard' },
    { icon: 'thermostat', label: 'Thermodynamics', id: 'AE-07', questions: 950, mastery: 76, difficulty: 'Medium' },
    { icon: 'calculate', label: 'Eng. Mathematics', id: 'AE-08', questions: 2640, mastery: 83, difficulty: 'Easy' },
]

const LandingPage = ({ onStart, onGetStarted, currentTheme, toggleTheme, user, onLogout }) => {
    const [subtitleIndex, setSubtitleIndex] = useState(0)

    useEffect(() => {
        const interval = setInterval(() => {
            setSubtitleIndex((prev) => (prev + 1) % CYCLING_SUBTITLES.length)
        }, 3000)
        return () => clearInterval(interval)
    }, [])

    return (
        <div className="bg-[#f5f7fb] dark:bg-[#050816] text-[#0f1629] dark:text-white font-lexend overflow-x-hidden antialiased selection:bg-landing-primary/30 selection:text-white min-h-screen flex flex-col transition-colors duration-300">
            {/* Top Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 border-b border-slate-200/60 dark:border-white/[0.04] bg-white/70 dark:bg-[#050816]/70 backdrop-blur-xl transition-colors duration-300">
                <div className="mx-auto max-w-[1200px] px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center size-8 rounded bg-landing-primary/10 dark:bg-landing-primary/20 text-landing-primary">
                            <span className="material-symbols-outlined text-[20px]">school</span>
                        </div>
                        <span className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">ExamPrep</span>
                    </div>
                    <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600 dark:text-slate-400">
                        <a href="#features" className="hover:text-landing-primary dark:hover:text-white transition-colors">Features</a>
                        <a href="#how-it-works" className="hover:text-landing-primary dark:hover:text-white transition-colors">How It Works</a>
                        <a href="#concepts" className="hover:text-landing-primary dark:hover:text-white transition-colors">Concepts</a>
                    </div>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={toggleTheme}
                            className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 transition-colors"
                            aria-label="Toggle Theme"
                        >
                            {currentTheme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                        </button>
                        {user ? (
                            <>
                                <div className="hidden sm:flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-300 px-3">
                                    <User size={16} />
                                    <span>{user.email}</span>
                                </div>
                                <button
                                    onClick={onLogout}
                                    className="flex items-center justify-center gap-2 h-9 px-4 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-white text-sm font-medium transition-all"
                                >
                                    <LogOut size={16} />
                                    <span className="hidden sm:inline">Logout</span>
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={onGetStarted}
                                className="flex items-center justify-center h-9 px-5 rounded-lg bg-landing-primary hover:bg-landing-primary/90 text-white text-sm font-semibold transition-all shadow-[0_0_15px_-3px_rgba(56,88,250,0.4)] hover:scale-[1.02]"
                                tabIndex={0}
                                aria-label="Get Started"
                            >
                                Get Started
                            </button>
                        )}
                    </div>
                </div>
            </nav>

            <main className="relative pt-16 flex flex-col items-center w-full flex-grow">
                {/* ===== HERO SECTION ===== */}
                <section className="relative w-full min-h-[90vh] flex items-center overflow-hidden">
                    {/* Light mode ambient gradients */}
                    <div className="absolute inset-0 dark:hidden pointer-events-none">
                        <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-gradient-to-br from-indigo-200/40 via-blue-100/30 to-transparent blur-3xl" />
                        <div className="absolute bottom-[-10%] left-[10%] w-[500px] h-[500px] rounded-full bg-gradient-to-tr from-purple-200/30 via-cyan-100/20 to-transparent blur-3xl" />
                        <div className="absolute top-[30%] left-[40%] w-[400px] h-[400px] rounded-full bg-gradient-to-b from-blue-100/25 to-transparent blur-3xl" />
                    </div>

                    {/* Dark mode atmospheric gradients */}
                    <div className="absolute inset-0 hidden dark:block pointer-events-none">
                        <div className="absolute inset-0 bg-gradient-to-b from-[#070B1F] via-[#050816] to-[#050816]" />
                        <div className="absolute top-[10%] left-[15%] w-[700px] h-[700px] rounded-full bg-[#4F7CFF]/[0.04] blur-[120px]" />
                        <div className="absolute top-[30%] right-[10%] w-[600px] h-[600px] rounded-full bg-[#00D1FF]/[0.03] blur-[100px]" />
                        <div className="absolute bottom-[10%] left-[30%] w-[500px] h-[500px] rounded-full bg-[#9B6DFF]/[0.035] blur-[110px]" />
                        <div className="absolute top-[50%] right-[25%] w-[400px] h-[400px] rounded-full bg-[#FF5FD2]/[0.02] blur-[100px]" />
                        <div className="absolute top-[20%] left-[35%] w-[300px] h-[300px] rounded-full bg-[#00D1FF]/[0.025] blur-[80px]" />
                    </div>

                    <div className="absolute inset-0">
                        <ParticleNetwork theme={currentTheme} />
                        <div className="absolute inset-0 bg-gradient-to-r from-[#f5f7fb]/80 via-[#f5f7fb]/40 to-transparent dark:from-[#050816]/60 dark:via-transparent dark:to-transparent pointer-events-none" />
                        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#f5f7fb] dark:from-[#050816] to-transparent pointer-events-none" />
                    </div>

                    <div className="absolute inset-0 hidden lg:block pointer-events-none">
                        {FLOATING_BADGES.map((badge, i) => (
                            <motion.div
                                key={badge.label}
                                className="absolute flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/60 dark:bg-white/10 backdrop-blur-lg border border-white/80 dark:border-white/10 shadow-[0_2px_12px_rgba(56,88,250,0.06)]"
                                style={{ top: badge.top, right: badge.right }}
                                animate={{ y: [0, -8, 0] }}
                                transition={{ duration: 3 + i * 0.5, repeat: Infinity, ease: 'easeInOut', delay: i * 0.4 }}
                            >
                                <span className="size-2 rounded-full" style={{ backgroundColor: badge.color }} />
                                <span className="text-xs font-medium text-slate-700 dark:text-white/80">{badge.label}</span>
                            </motion.div>
                        ))}
                    </div>

                    <div className="relative z-10 mx-auto max-w-[1200px] px-6 w-full">
                        <div className="max-w-[580px] flex flex-col gap-5">
                            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 dark:border-emerald-500/20 bg-emerald-500/10 dark:bg-emerald-500/5 px-4 py-1.5 backdrop-blur-md w-fit">
                                <span className="flex size-2 rounded-full bg-emerald-500 dark:bg-emerald-400 animate-pulse" />
                                <span className="text-xs font-mono font-medium text-emerald-600 dark:text-emerald-400 tracking-wide uppercase">Early Access — Free During Beta</span>
                            </div>

                            <h1 className="text-5xl md:text-7xl font-bold tracking-tighter leading-[1.05]">
                                <span className="text-[#0f1629] dark:text-white block">Master GATE</span>
                                <span className="hero-gradient-text block">Aerospace</span>
                            </h1>

                            <p className="text-lg text-[#3d4a63] dark:text-slate-400 leading-relaxed max-w-[500px]">
                                The most intelligent, data-driven platform built to make you an Aerospace engineer.
                            </p>

                            {/* Cycling subtitle */}
                            <div className="h-6 relative overflow-hidden">
                                <AnimatePresence mode="wait">
                                    <motion.span
                                        key={subtitleIndex}
                                        initial={{ y: 20, opacity: 0 }}
                                        animate={{ y: 0, opacity: 1 }}
                                        exit={{ y: -20, opacity: 0 }}
                                        transition={{ duration: 0.4, ease: 'easeInOut' }}
                                        className="absolute text-sm font-medium text-landing-primary dark:text-cyan-400"
                                    >
                                        {CYCLING_SUBTITLES[subtitleIndex]}
                                    </motion.span>
                                </AnimatePresence>
                            </div>

                            <div className="flex flex-wrap items-center gap-4 mt-2">
                                <button
                                    onClick={onStart}
                                    className="group flex items-center justify-center h-12 px-7 rounded-xl bg-landing-primary hover:bg-landing-primary/90 text-white font-semibold transition-all hover:scale-[1.02] shadow-[0_4px_20px_rgba(56,88,250,0.35),0_0_40px_rgba(56,88,250,0.15)]"
                                    tabIndex={0}
                                    aria-label="Start Your Journey"
                                >
                                    Start Your Journey
                                    <ArrowRight size={18} className="ml-2 group-hover:translate-x-1 transition-transform" />
                                </button>
                            </div>

                            {/* Credibility line */}
                            <div className="flex flex-wrap items-center gap-4 mt-3 text-xs font-medium text-slate-500 dark:text-slate-500">
                                <div className="flex items-center gap-1.5">
                                    <span className="material-symbols-outlined text-[14px] text-landing-primary">database</span>
                                    12,480+ PYQ questions
                                </div>
                                <span className="size-1 rounded-full bg-slate-300 dark:bg-slate-600" />
                                <div className="flex items-center gap-1.5">
                                    <span className="material-symbols-outlined text-[14px] text-landing-primary">category</span>
                                    8 core subjects
                                </div>
                                <span className="size-1 rounded-full bg-slate-300 dark:bg-slate-600" />
                                <div className="flex items-center gap-1.5">
                                    <span className="material-symbols-outlined text-[14px] text-landing-primary">history_edu</span>
                                    20 years of papers
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* ===== FEATURES GRID (6 cards) ===== */}
                <section id="features" className="w-full max-w-[1200px] px-6 py-24 relative z-10">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: '-100px' }}
                        transition={{ duration: 0.6 }}
                        className="text-center mb-16"
                    >
                        <h2 className="text-3xl md:text-5xl font-bold text-[#0f1629] dark:text-white mb-6 font-display tracking-tight">
                            Everything You Need. <span className="text-slate-400 dark:text-slate-500">Nothing You Don't.</span>
                        </h2>
                        <p className="text-lg text-[#3d4a63] dark:text-slate-400 max-w-2xl mx-auto">
                            Six integrated systems working together to take you from random solving to ranked performance.
                        </p>
                    </motion.div>

                    <div className="grid md:grid-cols-3 gap-6">
                        {FEATURES.map((feature, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true, margin: '-50px' }}
                                transition={{ duration: 0.4, delay: i * 0.08 }}
                                className="glass-panel rounded-2xl p-7 transition-all duration-300 group hover:-translate-y-1 hover:shadow-[0_12px_40px_rgba(56,88,250,0.08)] hover:border-landing-primary/20 dark:hover:border-landing-primary/30"
                            >
                                <div className="flex items-start justify-between mb-5">
                                    <div className="size-12 rounded-xl bg-gradient-to-br from-indigo-50 dark:from-landing-primary/10 to-transparent flex items-center justify-center text-landing-primary border border-indigo-100 dark:border-landing-primary/20 group-hover:scale-110 transition-transform shadow-sm">
                                        <span className="material-symbols-outlined text-[24px]">{feature.icon}</span>
                                    </div>
                                    <span className="text-[10px] font-mono font-medium text-slate-400 dark:text-slate-500 bg-slate-100 dark:bg-white/5 px-2 py-0.5 rounded-full">{feature.metric}</span>
                                </div>
                                <h3 className="text-lg font-bold text-[#0f1629] dark:text-white mb-2 group-hover:text-landing-primary transition-colors">
                                    {feature.title}
                                </h3>
                                <p className="text-[#3d4a63] dark:text-slate-400 leading-relaxed text-sm">{feature.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </section>

                {/* ===== HOW IT WORKS ===== */}
                <section id="how-it-works" className="w-full max-w-[900px] px-6 py-24 relative z-10">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: '-100px' }}
                        transition={{ duration: 0.6 }}
                        className="text-center mb-16"
                    >
                        <div className="text-xs font-mono text-landing-primary mb-3 uppercase tracking-widest">The System</div>
                        <h2 className="text-3xl md:text-5xl font-bold text-[#0f1629] dark:text-white tracking-tight">
                            How It Works
                        </h2>
                    </motion.div>

                    <div className="relative">
                        {/* Connecting line */}
                        <div className="absolute left-[28px] md:left-1/2 md:-translate-x-px top-0 bottom-0 w-px bg-gradient-to-b from-landing-primary/40 via-landing-primary/20 to-transparent hidden sm:block" />

                        <div className="flex flex-col gap-16">
                            {HOW_IT_WORKS.map((item, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, x: i % 2 === 0 ? -30 : 30 }}
                                    whileInView={{ opacity: 1, x: 0 }}
                                    viewport={{ once: true, margin: '-80px' }}
                                    transition={{ duration: 0.5, delay: i * 0.15 }}
                                    className={`relative flex items-start gap-6 md:gap-12 ${i % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'} md:text-${i % 2 === 0 ? 'right' : 'left'}`}
                                >
                                    {/* Content */}
                                    <div className={`flex-1 ${i % 2 === 0 ? 'md:text-right' : 'md:text-left'}`}>
                                        <h3 className="text-xl font-bold text-[#0f1629] dark:text-white mb-2">{item.title}</h3>
                                        <p className="text-sm text-[#3d4a63] dark:text-slate-400 leading-relaxed">{item.desc}</p>
                                    </div>

                                    {/* Node */}
                                    <div className="relative flex-shrink-0 flex items-center justify-center">
                                        <div className="size-14 rounded-full bg-landing-primary/10 dark:bg-landing-primary/20 border-2 border-landing-primary/30 flex items-center justify-center shadow-[0_0_20px_rgba(56,88,250,0.15)]">
                                            <span className="text-sm font-bold text-landing-primary font-mono">{item.step}</span>
                                        </div>
                                        <div className="absolute inset-0 rounded-full bg-landing-primary/5 animate-ping opacity-30" />
                                    </div>

                                    {/* Spacer for alignment */}
                                    <div className="flex-1 hidden md:block" />
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* ===== CONCEPTS SECTION ===== */}
                <section id="concepts" className="py-24 px-6 w-full max-w-[1100px] relative z-10">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: '-100px' }}
                        transition={{ duration: 0.6 }}
                        className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10 border-b border-dashed border-slate-200 dark:border-slate-800 pb-6"
                    >
                        <div>
                            <div className="text-xs font-mono text-landing-primary mb-2 uppercase tracking-widest">Subject Modules</div>
                            <h3 className="text-3xl font-bold tracking-tight text-[#0f1629] dark:text-white">Explore by Concept</h3>
                        </div>
                        <button
                            onClick={onStart}
                            className="text-landing-primary hover:text-white hover:bg-landing-primary px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-all border border-landing-primary/20"
                            tabIndex={0}
                            aria-label="View All Modules"
                        >
                            View All Modules
                            <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
                        </button>
                    </motion.div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {CONCEPTS.map((item, i) => (
                            <motion.button
                                key={i}
                                initial={{ opacity: 0, y: 15 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.3, delay: i * 0.05 }}
                                onClick={onStart}
                                className="group flex flex-col justify-between p-5 h-40 rounded-xl text-left glass-panel transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgba(56,88,250,0.08)] hover:border-landing-primary/20"
                                tabIndex={0}
                                aria-label={item.label}
                            >
                                <div className="flex justify-between items-start w-full">
                                    <span className="material-symbols-outlined text-slate-400 dark:text-slate-500 group-hover:text-landing-primary transition-colors text-[26px]">{item.icon}</span>
                                    <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded ${
                                        item.difficulty === 'Hard' ? 'text-red-500 bg-red-50 dark:bg-red-500/10' :
                                        item.difficulty === 'Medium' ? 'text-amber-500 bg-amber-50 dark:bg-amber-500/10' :
                                        'text-emerald-500 bg-emerald-50 dark:bg-emerald-500/10'
                                    }`}>{item.difficulty}</span>
                                </div>
                                <div className="mt-auto">
                                    <span className="font-bold text-slate-700 dark:text-slate-200 group-hover:text-landing-primary transition-colors block leading-tight text-sm">{item.label}</span>
                                    <div className="flex items-center justify-between mt-2">
                                        <span className="text-[10px] font-mono text-slate-400">{item.questions} Qs</span>
                                        <span className="text-[10px] font-mono text-landing-primary">{item.mastery}%</span>
                                    </div>
                                    <div className="h-1 w-full bg-slate-200 dark:bg-slate-700 mt-1.5 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-landing-primary rounded-full group-hover:bg-gradient-to-r group-hover:from-landing-primary group-hover:to-cyan-400 transition-all duration-700"
                                            style={{ width: `${item.mastery}%` }}
                                        />
                                    </div>
                                </div>
                            </motion.button>
                        ))}
                    </div>
                </section>

                {/* ===== CTA SECTION ===== */}
                <section className="w-full py-32 px-6 relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-b from-indigo-50/50 via-white to-indigo-50/30 dark:from-[#070B1F] dark:via-[#050816] dark:to-[#0A1028] border-y border-indigo-100/50 dark:border-white/[0.04]">
                        <div className="absolute inset-0 tech-grid-bg opacity-[0.03] dark:opacity-10" />
                        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-landing-primary/[0.02] dark:via-landing-primary/5 to-transparent" />
                    </div>
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: '-100px' }}
                        transition={{ duration: 0.6 }}
                        className="relative z-10 max-w-3xl mx-auto text-center flex flex-col items-center"
                    >
                        <h2 className="text-3xl md:text-5xl font-bold mb-6 tracking-tighter text-[#0f1629] dark:text-white leading-tight">
                            Stop Solving Random Questions.<br />
                            <span className="text-landing-primary">Start Training Intelligently.</span>
                        </h2>
                        <p className="text-lg text-[#3d4a63] dark:text-slate-400 mb-10 max-w-xl mx-auto leading-relaxed">
                            Your AIR doesn't depend on motivation. It depends on systems. Join the smartest preparation engine for GATE Aerospace.
                        </p>
                        <button
                            onClick={onStart}
                            className="group relative flex items-center justify-center h-14 text-base px-10 rounded-xl bg-landing-primary text-white font-bold tracking-tight transition-all hover:scale-[1.02] shadow-[0_4px_20px_rgba(56,88,250,0.4),0_0_50px_rgba(56,88,250,0.15)] overflow-hidden"
                            tabIndex={0}
                            aria-label="Start Free"
                        >
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:animate-shine" />
                            <span className="relative z-10 flex items-center gap-2">
                                Start Free — No Card Required
                                <span className="material-symbols-outlined text-[18px] group-hover:translate-x-1 transition-transform">arrow_forward</span>
                            </span>
                        </button>
                    </motion.div>
                </section>
            </main>

            {/* ===== FOOTER ===== */}
            <footer className="w-full relative">
                <div className="h-px bg-gradient-to-r from-transparent via-landing-primary/30 to-transparent" />
                <div className="bg-white/50 dark:bg-slate-900/50 py-12 px-6 backdrop-blur-sm">
                    <div className="mx-auto max-w-[1200px]">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
                            {/* Brand */}
                            <div className="md:col-span-1">
                                <div className="flex items-center gap-2 mb-3">
                                    <div className="flex items-center justify-center size-7 rounded bg-landing-primary/10 text-landing-primary">
                                        <span className="material-symbols-outlined text-[16px]">school</span>
                                    </div>
                                    <span className="text-sm font-bold text-slate-900 dark:text-white">ExamPrep</span>
                                </div>
                                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed italic">
                                    Built for engineers who think deeply.
                                </p>
                            </div>

                            {/* Product */}
                            <div>
                                <h4 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-3">Product</h4>
                                <div className="flex flex-col gap-2 text-xs text-slate-500 dark:text-slate-400">
                                    <a href="#features" className="hover:text-landing-primary transition-colors">Features</a>
                                    <a href="#concepts" className="hover:text-landing-primary transition-colors">Concepts</a>
                                    <button onClick={onStart} className="text-left hover:text-landing-primary transition-colors">CBT Simulator</button>
                                    <button onClick={onStart} className="text-left hover:text-landing-primary transition-colors">Pricing</button>
                                </div>
                            </div>

                            {/* Resources */}
                            <div>
                                <h4 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-3">Resources</h4>
                                <div className="flex flex-col gap-2 text-xs text-slate-500 dark:text-slate-400">
                                    <a href="#" className="hover:text-landing-primary transition-colors">GATE Syllabus</a>
                                    <a href="#" className="hover:text-landing-primary transition-colors">Formula Sheets</a>
                                    <a href="#" className="hover:text-landing-primary transition-colors">Study Plans</a>
                                    <a href="#" className="hover:text-landing-primary transition-colors">Blog</a>
                                </div>
                            </div>

                            {/* Legal */}
                            <div>
                                <h4 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-3">Legal</h4>
                                <div className="flex flex-col gap-2 text-xs text-slate-500 dark:text-slate-400">
                                    <a href="#" className="hover:text-landing-primary transition-colors">Privacy Policy</a>
                                    <a href="#" className="hover:text-landing-primary transition-colors">Terms of Service</a>
                                    <a href="#" className="hover:text-landing-primary transition-colors">Contact</a>
                                </div>
                            </div>
                        </div>

                        <div className="border-t border-slate-200/60 dark:border-white/5 pt-6 flex flex-col md:flex-row items-center justify-between gap-4 text-xs font-medium text-slate-400 dark:text-slate-500">
                            <div className="flex items-center gap-2">
                                <span className="size-2 rounded-full bg-emerald-500" />
                                <span>All Systems Normal</span>
                            </div>
                            <div>© 2025 ExamPrep. All rights reserved.</div>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    )
}

export default LandingPage
