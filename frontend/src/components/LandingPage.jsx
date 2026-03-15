import { Moon, Sun, LogOut, User } from 'lucide-react';

const LandingPage = ({ onStart, onLogin, onRegister, currentTheme, toggleTheme, user, onLogout }) => {
    return (
        <div className="bg-landing-bg-light dark:bg-landing-bg-dark text-slate-900 dark:text-white font-lexend overflow-x-hidden antialiased selection:bg-landing-primary/30 selection:text-white min-h-screen flex flex-col transition-colors duration-300">
            {/* Top Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 border-b border-landing-border/20 dark:border-landing-border/50 bg-white/80 dark:bg-landing-bg-dark/80 backdrop-blur-md transition-colors duration-300">
                <div className="mx-auto max-w-[1200px] px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center size-8 rounded bg-landing-primary/10 dark:bg-landing-primary/20 text-landing-primary">
                            <span className="material-symbols-outlined text-[20px]">school</span>
                        </div>
                        <span className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">ExamPrep</span>
                    </div>
                    <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600 dark:text-slate-400">
                        <a href="#features" className="hover:text-landing-primary dark:hover:text-white transition-colors">Features</a>
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
                                    className="flex items-center justify-center gap-2 h-9 px-4 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-white text-sm font-medium transition-all">
                                    <LogOut size={16} />
                                    <span className="hidden sm:inline">Logout</span>
                                </button>
                            </>
                        ) : (
                            <>
                                <button
                                    onClick={onLogin}
                                    className="hidden sm:block text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-landing-primary dark:hover:text-white px-4 transition-colors">
                                    Login
                                </button>
                                <button
                                    onClick={onRegister || onStart}
                                    className="flex items-center justify-center h-9 px-4 rounded-lg bg-landing-primary hover:bg-landing-primary/90 text-white text-sm font-semibold transition-all shadow-[0_0_15px_-3px_rgba(56,88,250,0.4)]">
                                    Sign Up
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </nav>

            <main className="relative pt-16 flex flex-col items-center w-full flex-grow">
                {/* Hero Section */}
                {/* Hero Section */}
                <section className="relative w-full flex flex-col items-center justify-center pt-24 pb-16 px-6 overflow-hidden min-h-[85vh] bg-gradient-to-br from-blue-900/20 to-transparent">
                    {/* Technical Grid Background */}
                    <div className="absolute inset-0 tech-grid-bg pointer-events-none opacity-50 dark:opacity-40"></div>
                    <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-landing-primary/20 blur-[120px] rounded-full pointer-events-none opacity-30"></div>
                    <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-purple-500/20 blur-[120px] rounded-full pointer-events-none opacity-30"></div>

                    <div className="relative z-10 max-w-[900px] flex flex-col items-center text-center gap-8">
                        <div className="inline-flex items-center gap-2 rounded-full border border-landing-primary/20 bg-landing-primary/5 px-4 py-1.5 backdrop-blur-md">
                            <span className="flex size-2 rounded-full bg-landing-primary animate-pulse"></span>
                            <span className="text-xs font-mono font-medium text-landing-primary tracking-wide uppercase">System Operational</span>
                        </div>

                        <h1 className="text-5xl md:text-8xl font-bold tracking-tighter leading-[1] text-slate-900 dark:text-white">
                            Master GATE Aerospace with <span className="gradient-text-animate">Precision Engineering</span>.
                        </h1>

                        <p className="text-xl text-slate-600 dark:text-slate-400 max-w-[600px] leading-relaxed font-light">
                            Drill down into specific topics, access 20+ years of archived data, and track your technical mastery in real-time.
                        </p>

                        <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto mt-6">
                            <button
                                onClick={onStart}
                                className="group relative flex items-center justify-center h-16 text-lg px-10 py-5 rounded-lg bg-landing-primary text-white font-bold tracking-tight transition-all hover:scale-[1.02] shadow-[0_0_20px_rgba(37,99,235,0.5)] overflow-hidden">
                                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:animate-shine" />
                                <span className="relative z-10 flex items-center gap-2">
                                    Start 7-Day Free Trial
                                    <span className="material-symbols-outlined text-[20px] group-hover:translate-x-1 transition-transform">arrow_forward</span>
                                </span>
                            </button>
                        </div>
                        
                        {/* Stats Ribbon */}
                        <div className="flex flex-wrap items-center justify-center gap-6 mt-8 text-sm font-medium text-slate-600 dark:text-slate-400">
                            <div className="flex items-center gap-2">
                                <span className="material-symbols-outlined text-landing-primary text-[18px]">verified</span>
                                1500+ Questions
                            </div>
                            <div className="hidden sm:block size-1 rounded-full bg-landing-border dark:bg-landing-border/50"></div>
                            <div className="flex items-center gap-2">
                                <span className="material-symbols-outlined text-landing-primary text-[18px]">analytics</span>
                                Topic-wise Analytics
                            </div>
                            <div className="hidden sm:block size-1 rounded-full bg-landing-border dark:bg-landing-border/50"></div>
                            <div className="flex items-center gap-2">
                                <span className="material-symbols-outlined text-landing-primary text-[18px]">history_edu</span>
                                20+ Years of Papers
                            </div>
                        </div>
                    </div>

                    {/* Flight Data Recorder HUD Preview */}
                    <div className="mt-24 w-full max-w-[1000px] relative z-10 perspective-[1000px]">
                        <div className="hud-panel rounded-xl border border-landing-border/20 backdrop-blur-xl transform rotate-x-[10deg] transition-transform duration-700 hover:rotate-x-0 shadow-2xl">
                            {/* HUD Header */}
                            <div className="h-10 border-b border-landing-primary/20 flex items-center justify-between px-4 bg-slate-900/50">
                                <div className="flex items-center gap-4 text-xs font-mono text-landing-primary/80">
                                    <span>REC: ON</span>
                                    <span>FLT_MODE: TEST</span>
                                    <span>ALT: 35,000</span>
                                </div>
                                <div className="flex gap-2">
                                    <div className="size-2 rounded-full bg-red-500/50 animate-pulse"></div>
                                    <div className="size-2 rounded-full bg-yellow-500/50"></div>
                                    <div className="size-2 rounded-full bg-green-500/50"></div>
                                </div>
                            </div>

                            {/* HUD Content */}
                            <div className="p-8 grid grid-cols-1 md:grid-cols-3 gap-8 divide-y md:divide-y-0 md:divide-x divide-landing-primary/20 text-white">
                                <div className="flex flex-col gap-2 px-4 items-center text-center">
                                    <div className="text-landing-primary/80 font-mono text-xs mb-2 tracking-[0.2em] uppercase">Data Points</div>
                                    <p className="text-5xl font-bold tracking-tighter hud-metric">14,000<span className="text-lg text-landing-primary">+</span></p>
                                    <p className="text-xs text-slate-400 font-mono uppercase tracking-widest mt-2">Questions Indexed</p>
                                </div>
                                <div className="flex flex-col gap-2 px-4 items-center text-center">
                                    <div className="text-purple-400/80 font-mono text-xs mb-2 tracking-[0.2em] uppercase">Archive Depth</div>
                                    <p className="text-5xl font-bold tracking-tighter hud-metric">10<span className="text-lg text-purple-400">+</span></p>
                                    <p className="text-xs text-slate-400 font-mono uppercase tracking-widest mt-2">Years History</p>
                                </div>
                                <div className="flex flex-col gap-2 px-4 items-center text-center">
                                    <div className="text-emerald-400/80 font-mono text-xs mb-2 tracking-[0.2em] uppercase">Telemetry</div>
                                    <p className="text-5xl font-bold tracking-tighter hud-metric">500<span className="text-lg text-emerald-400">+</span></p>
                                    <p className="text-xs text-slate-400 font-mono uppercase tracking-widest mt-2">Concepts Mapped</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Features Grid */}
                <div id="features" className="w-full max-w-[1200px] px-6 py-24 relative z-10">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-5xl font-bold text-slate-900 dark:text-white mb-6 font-display tracking-tight">
                            Built for Engineers, <span className="text-slate-500 line-through decoration-red-500 decoration-2">Not Robots</span>.
                        </h2>
                        <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto border-l-2 border-landing-primary pl-4 italic">
                            "Traditional prep is chaotic. We bring structure to the madness."
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            {
                                icon: "hub",
                                title: "Topic-Based Learning",
                                desc: "Don't just solve papers. Solve specific weaknesses. We index every question by concept, so you can focus on what matters."
                            },
                            {
                                icon: "history_edu",
                                title: "20 Years of Papers",
                                desc: "Access the most comprehensive archive of GATE Aerospace questions, cleanly formatted and ready to solve."
                            },
                            {
                                icon: "insights",
                                title: "Real-Time Telemetry",
                                desc: "Track your accuracy, speed, and topic mastery. Know exactly where you stand before exam day."
                            }
                        ].map((feature, i) => (
                            <div key={i} className="glass-panel glass-panel-hover rounded-2xl p-8 transition-all duration-300 group dark:backdrop-blur-md dark:border-white/10 dark:bg-white/5">
                                <div className="size-14 rounded-2xl bg-gradient-to-br from-landing-primary/10 to-transparent flex items-center justify-center text-landing-primary border border-landing-primary/20 mb-6 group-hover:scale-110 transition-transform shadow-lg shadow-landing-primary/5">
                                    <span className="material-symbols-outlined text-[28px]">{feature.icon}</span>
                                </div>
                                <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
                                    {feature.title}
                                    <span className="opacity-0 group-hover:opacity-100 transition-opacity text-landing-primary material-symbols-outlined text-sm">arrow_forward</span>
                                </h3>
                                <p className="text-slate-600 dark:text-slate-400 leading-relaxed text-sm">{feature.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Popular Concepts Section */}
                <section id="concepts" className="py-24 px-6 w-full max-w-[1000px] relative z-10">
                    <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10 border-b border-dashed border-slate-200 dark:border-slate-800 pb-6">
                        <div>
                            <div className="text-xs font-mono text-landing-primary mb-2 uppercase tracking-widest">System Modules</div>
                            <h3 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Popular Concepts</h3>
                        </div>
                        <button onClick={onStart} className="text-landing-primary hover:text-white hover:bg-landing-primary px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-all border border-landing-primary/20">
                            View All Modules
                            <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
                        </button>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {/* Concept Items - Curated Aerospace Topics */}
                        {[
                            { icon: "air", label: "Aerodynamics", id: "AE-01" },
                            { icon: "flight", label: "Flight Mechanics", id: "AE-02" },
                            { icon: "rocket_launch", label: "Propulsion", id: "AE-03" },
                            { icon: "construction", label: "Structures", id: "AE-04" },
                            { icon: "satellite_alt", label: "Space Dynamics", id: "AE-05" },
                            { icon: "water_drop", label: "Fluid Mechanics", id: "AE-06" },
                            { icon: "thermostat", label: "Thermodynamics", id: "AE-07" },
                            { icon: "calculate", label: "Eng. Math", id: "AE-08" }
                        ].map((item, i) => (
                            <button
                                key={i}
                                onClick={onStart}
                                className="instrument-card group flex flex-col justify-between p-5 h-32 rounded-lg text-left"
                            >
                                <div className="flex justify-between items-start width-full">
                                    <span className="material-symbols-outlined text-slate-400 dark:text-slate-500 group-hover:text-landing-primary transition-colors text-[28px]">{item.icon}</span>
                                    <span className="text-[10px] font-mono text-slate-400 opacity-50">{item.id}</span>
                                </div>
                                <div>
                                    <span className="font-bold text-slate-700 dark:text-slate-200 group-hover:text-landing-primary transition-colors block leading-tight">{item.label}</span>
                                    <div className="h-1 w-8 bg-slate-200 dark:bg-slate-700 mt-3 rounded-full overflow-hidden">
                                        <div className="h-full bg-landing-primary w-[60%] group-hover:w-full transition-all duration-500"></div>
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>
                </section>

                {/* CTA Section */}
                <section className="w-full py-32 px-6 relative overflow-hidden">
                    <div className="absolute inset-0 bg-slate-900/50 dark:bg-slate-900/20 border-y border-landing-primary/10">
                        <div className="absolute inset-0 tech-grid-bg opacity-10"></div>
                        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-landing-primary/5 to-transparent"></div>
                    </div>
                    <div className="relative z-10 max-w-4xl mx-auto text-center flex flex-col items-center">
                        <h2 className="text-4xl md:text-6xl font-bold mb-8 tracking-tighter text-slate-900 dark:text-white">
                            Ready for Liftoff?
                        </h2>
                        <p className="text-xl text-slate-600 dark:text-slate-400 mb-10 max-w-2xl mx-auto font-light">
                            Join thousands of aspirants practicing smarter, not harder. System status: GO for launch.
                        </p>
                        <button
                            onClick={onStart}
                            className="group relative flex items-center justify-center h-16 text-lg px-10 py-5 rounded-lg bg-landing-primary text-white font-bold tracking-tight transition-all hover:scale-[1.02] shadow-[0_0_20px_rgba(37,99,235,0.5)] overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:animate-shine" />
                            <span className="relative z-10 flex items-center gap-2">
                                Start 7-Day Free Trial
                                <span className="material-symbols-outlined text-[20px] group-hover:translate-x-1 transition-transform">arrow_forward</span>
                            </span>
                        </button>
                        <p className="text-xs text-slate-500 dark:text-slate-600 mt-6 font-mono">NO_CREDIT_CARD_REQUIRED // BASIC_PLAN_ACCESS_GRANTED</p>
                    </div>
                </section>
            </main>

            {/* Minimul Footer */}
            <footer className="w-full border-t border-slate-200 dark:border-white/5 bg-slate-50 dark:bg-slate-900/50 py-6 px-6 backdrop-blur-sm">
                <div className="mx-auto max-w-[1200px] flex flex-col md:flex-row items-center justify-between gap-4 text-xs font-medium text-slate-500 dark:text-slate-400">
                    <div className="flex items-center gap-2">
                        <span className="size-2 rounded-full bg-emerald-500"></span>
                        <span>All Systems Normal</span>
                    </div>
                    <div>
                        © 2023 ExamPrep Inc.
                    </div>
                    <div className="flex gap-6">
                        <a href="#" className="hover:text-landing-primary transition-colors">Contact</a>
                        <a href="#" className="hover:text-landing-primary transition-colors">Twitter</a>
                        <a href="#" className="hover:text-landing-primary transition-colors">GitHub</a>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
