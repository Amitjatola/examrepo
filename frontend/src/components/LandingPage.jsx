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
                        <button onClick={() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })} className="hover:text-landing-primary dark:hover:text-white transition-colors">About Us</button>
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
                <section className="relative w-full flex flex-col items-center justify-center pt-24 pb-16 px-6 overflow-hidden">
                    {/* Background effects */}
                    <div className="absolute inset-0 bg-grid-pattern [mask-image:linear-gradient(to_bottom,black,transparent)] dark:[mask-image:linear-gradient(to_bottom,white,transparent)] pointer-events-none opacity-50 dark:opacity-100"></div>
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-landing-primary/10 dark:bg-landing-primary/20 blur-[100px] rounded-full pointer-events-none opacity-50"></div>

                    <div className="relative z-10 max-w-[800px] flex flex-col items-center text-center gap-6">
                        <div className="inline-flex items-center gap-2 rounded-full border border-landing-border/20 dark:border-landing-border bg-white/50 dark:bg-landing-surface/50 px-3 py-1 mb-4 backdrop-blur-sm">
                            <span className="flex size-2 rounded-full bg-green-500 animate-pulse"></span>
                            <span className="text-xs font-medium text-slate-600 dark:text-slate-300">New Questions Added Daily</span>
                        </div>
                        <h1 className="text-5xl md:text-7xl font-bold tracking-[-0.03em] leading-[1.1] text-slate-900 dark:text-transparent dark:bg-clip-text dark:bg-gradient-to-b dark:from-white dark:to-white/60">
                            Master Concepts.<br />Conquer Exams.
                        </h1>
                        <p className="text-lg text-slate-600 dark:text-slate-400 max-w-[540px] leading-relaxed">
                            The precision tool for serious students. Drill down into specific concepts, access thousands of past questions, and track your mastery in real-time.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto mt-4">
                            <button
                                onClick={onStart}
                                className="flex items-center justify-center h-12 px-6 rounded-lg bg-landing-primary text-white font-semibold transition-all hover:scale-105 shadow-[0_0_20px_-5px_rgba(56,88,250,0.5)]">
                                Start Practicing Now
                                <span className="material-symbols-outlined ml-2 text-[20px]">arrow_forward</span>
                            </button>
                            <button
                                onClick={() => document.getElementById('concepts')?.scrollIntoView({ behavior: 'smooth' })}
                                className="flex items-center justify-center h-12 px-6 rounded-lg border border-landing-border/20 dark:border-landing-border bg-white dark:bg-landing-surface hover:bg-slate-50 dark:hover:bg-landing-border text-slate-700 dark:text-white font-medium transition-colors">
                                <span className="material-symbols-outlined mr-2 text-[20px] text-slate-400">search</span>
                                Browse Concepts
                            </button>
                        </div>
                    </div>

                    {/* Dashboard/Stats Preview */}
                    <div className="mt-20 w-full max-w-[1000px] relative z-10">
                        <div className="absolute -inset-1 bg-gradient-to-r from-landing-primary/20 to-purple-500/20 rounded-xl blur opacity-30"></div>
                        <div className="relative rounded-xl border border-landing-border/20 dark:border-landing-border bg-white/90 dark:bg-[#0f1323]/90 backdrop-blur-xl overflow-hidden shadow-2xl">
                            {/* Fake browser chrome */}
                            <div className="h-10 border-b border-landing-border/20 dark:border-landing-border flex items-center px-4 gap-2 bg-slate-50/50 dark:bg-landing-surface/50">
                                <div className="size-3 rounded-full bg-red-500/20 border border-red-500/50"></div>
                                <div className="size-3 rounded-full bg-yellow-500/20 border border-yellow-500/50"></div>
                                <div className="size-3 rounded-full bg-green-500/20 border border-green-500/50"></div>
                                <div className="ml-4 h-5 w-64 rounded bg-slate-200/50 dark:bg-white/5"></div>
                            </div>
                            {/* Stats Content inside "window" */}
                            <div className="p-8 grid grid-cols-1 md:grid-cols-3 gap-8 divide-y md:divide-y-0 md:divide-x divide-landing-border/10 dark:divide-landing-border">
                                <div className="flex flex-col gap-2 px-4 items-center text-center">
                                    <div className="p-3 rounded-lg bg-landing-primary/10 text-landing-primary mb-2">
                                        <span className="material-symbols-outlined text-[32px]">library_books</span>
                                    </div>
                                    <p className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">14,000+</p>
                                    <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">Questions Available</p>
                                </div>
                                <div className="flex flex-col gap-2 px-4 items-center text-center">
                                    <div className="p-3 rounded-lg bg-purple-500/10 text-purple-600 dark:text-purple-400 mb-2">
                                        <span className="material-symbols-outlined text-[32px]">history_edu</span>
                                    </div>
                                    <p className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">10+ Years</p>
                                    <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">Past Papers Archived</p>
                                </div>
                                <div className="flex flex-col gap-2 px-4 items-center text-center">
                                    <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 mb-2">
                                        <span className="material-symbols-outlined text-[32px]">category</span>
                                    </div>
                                    <p className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">500+</p>
                                    <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">Concepts Indexed</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Features Section */}
                <section id="features" className="py-24 px-6 w-full bg-white dark:bg-landing-surface border-y border-landing-border/10 dark:border-landing-border transition-colors duration-300">
                    <div className="mx-auto max-w-[1000px]">
                        <div className="mb-12">
                            <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white mb-4">Why Top Students Choose ExamPrep</h2>
                            <p className="text-slate-600 dark:text-slate-400 max-w-[600px]">We don't just give you questions. We give you a structured path to mastery through concept-based learning and analytics.</p>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Card 1 */}
                            <div className="group relative p-6 rounded-xl bg-slate-50 dark:bg-landing-bg-dark border border-slate-200 dark:border-landing-border hover:border-landing-primary/50 transition-all duration-300">
                                <div className="absolute inset-0 bg-gradient-to-br from-landing-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-xl"></div>
                                <div className="relative z-10 flex flex-col gap-4">
                                    <div className="size-12 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-600 dark:text-blue-400 border border-blue-500/20">
                                        <span className="material-symbols-outlined">hub</span>
                                    </div>
                                    <h3 className="text-xl font-bold text-slate-900 dark:text-white">Concept-First Architecture</h3>
                                    <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                                        Don't just practice randomly. Our engine groups questions by underlying theory, allowing you to target weak spots precisely.
                                    </p>
                                </div>
                            </div>
                            {/* Card 2 */}
                            <div className="group relative p-6 rounded-xl bg-slate-50 dark:bg-landing-bg-dark border border-slate-200 dark:border-landing-border hover:border-purple-500/50 transition-all duration-300">
                                <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-xl"></div>
                                <div className="relative z-10 flex flex-col gap-4">
                                    <div className="size-12 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-600 dark:text-purple-400 border border-purple-500/20">
                                        <span className="material-symbols-outlined">inventory_2</span>
                                    </div>
                                    <h3 className="text-xl font-bold text-slate-900 dark:text-white">Deep Archives</h3>
                                    <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                                        Access a decade of high-fidelity past papers. Every question is tagged, indexed, and ready for your custom problem sets.
                                    </p>
                                </div>
                            </div>
                            {/* Card 3 */}
                            <div className="group relative p-6 rounded-xl bg-slate-50 dark:bg-landing-bg-dark border border-slate-200 dark:border-landing-border hover:border-emerald-500/50 transition-all duration-300">
                                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-xl"></div>
                                <div className="relative z-10 flex flex-col gap-4">
                                    <div className="size-12 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                                        <span className="material-symbols-outlined">lightbulb</span>
                                    </div>
                                    <h3 className="text-xl font-bold text-slate-900 dark:text-white">Instant Insights</h3>
                                    <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                                        Get detailed, step-by-step solutions instantly. Understand the 'why' behind the answer, not just the 'what'.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Popular Concepts Section */}
                <section id="concepts" className="py-24 px-6 w-full max-w-[1000px]">
                    <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
                        <div>
                            <h3 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Popular Concepts</h3>
                            <p className="text-slate-600 dark:text-slate-400 mt-2">Jump straight into the most practiced topics this week.</p>
                        </div>
                        <button onClick={onStart} className="text-landing-primary hover:text-landing-primary/80 font-medium text-sm flex items-center gap-1 group">
                            View all 500+ concepts
                            <span className="material-symbols-outlined text-[16px] group-hover:translate-x-1 transition-transform">arrow_forward</span>
                        </button>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {/* Concept Items */}
                        {[
                            { icon: "functions", label: "Calculus III" },
                            { icon: "biotech", label: "Organic Chem" },
                            { icon: "balance", label: "Macroeconomics" },
                            { icon: "terminal", label: "Data Structures" },
                            { icon: "psychology", label: "Cognitive Psych" },
                            { icon: "gavel", label: "Contract Law" },
                            { icon: "calculate", label: "Statistics" },
                            { icon: "public", label: "World History" }
                        ].map((item, i) => (
                            <button
                                key={i}
                                onClick={onStart}
                                className="group flex flex-col justify-between p-4 h-28 rounded-lg border border-slate-200 dark:border-landing-border bg-white dark:bg-landing-surface hover:bg-slate-50 dark:hover:bg-landing-border/50 transition-colors text-left shadow-sm"
                            >
                                <span className="material-symbols-outlined text-slate-400 dark:text-slate-500 group-hover:text-landing-primary dark:group-hover:text-white transition-colors">{item.icon}</span>
                                <span className="font-medium text-slate-700 dark:text-slate-300 group-hover:text-landing-primary dark:group-hover:text-white">{item.label}</span>
                            </button>
                        ))}
                    </div>
                </section>

                {/* CTA Section */}
                <section className="py-20 w-full px-6 border-t border-landing-border/10 dark:border-landing-border bg-landing-bg-dark relative overflow-hidden">
                    <div className="absolute inset-0 bg-grid-pattern opacity-30 pointer-events-none"></div>
                    <div className="relative z-10 max-w-[800px] mx-auto text-center flex flex-col items-center gap-6">
                        <h2 className="text-3xl md:text-5xl font-bold text-white tracking-tight">Ready to boost your grades?</h2>
                        <p className="text-slate-400 text-lg max-w-[500px]">Join thousands of students mastering their subjects one concept at a time.</p>
                        <div className="mt-4">
                            <button
                                onClick={onStart}
                                className="h-12 px-8 rounded-lg bg-white text-landing-bg-dark font-bold text-lg hover:bg-slate-200 transition-colors">
                                Get Started for Free
                            </button>
                        </div>
                        <p className="text-xs text-slate-600 mt-4">No credit card required for basic plan.</p>
                    </div>
                </section>
            </main>

            {/* Footer */}
            <footer className="w-full border-t border-slate-200 dark:border-landing-border bg-slate-50 dark:bg-landing-bg-dark py-12 px-6 transition-colors duration-300">
                <div className="mx-auto max-w-[1200px] flex flex-col md:flex-row justify-between gap-12">
                    <div className="flex flex-col gap-4">
                        <div className="flex items-center gap-2 text-slate-900 dark:text-white font-bold text-lg">
                            <span className="material-symbols-outlined text-landing-primary">school</span>
                            ExamPrep
                        </div>
                        <p className="text-sm text-slate-600 dark:text-slate-500 max-w-[240px]">
                            The data-driven platform for academic excellence.
                        </p>
                        <div className="flex gap-4 mt-2">
                            <a href="#" className="text-slate-400 hover:text-landing-primary dark:text-slate-500 dark:hover:text-white transition-colors"><span className="material-symbols-outlined">laptop_mac</span></a>
                            <a href="#" className="text-slate-400 hover:text-landing-primary dark:text-slate-500 dark:hover:text-white transition-colors"><span className="material-symbols-outlined">mail</span></a>
                        </div>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-12 text-sm">
                        <div className="flex flex-col gap-4">
                            <h4 className="font-bold text-slate-900 dark:text-white">Product</h4>
                            <a href="#" className="text-slate-600 hover:text-landing-primary dark:text-slate-500 dark:hover:text-white transition-colors">Features</a>
                            <a href="#" className="text-slate-600 hover:text-landing-primary dark:text-slate-500 dark:hover:text-white transition-colors">Pricing</a>
                            <a href="#" className="text-slate-600 hover:text-landing-primary dark:text-slate-500 dark:hover:text-white transition-colors">Changelog</a>
                        </div>
                        <div className="flex flex-col gap-4">
                            <h4 className="font-bold text-slate-900 dark:text-white">Resources</h4>
                            <a href="#" className="text-slate-600 hover:text-landing-primary dark:text-slate-500 dark:hover:text-white transition-colors">Study Guides</a>
                            <a href="#" className="text-slate-600 hover:text-landing-primary dark:text-slate-500 dark:hover:text-white transition-colors">Concept Index</a>
                            <a href="#" className="text-slate-600 hover:text-landing-primary dark:text-slate-500 dark:hover:text-white transition-colors">API</a>
                        </div>
                        <div className="flex flex-col gap-4">
                            <h4 className="font-bold text-slate-900 dark:text-white">Company</h4>
                            <a href="#" className="text-slate-600 hover:text-landing-primary dark:text-slate-500 dark:hover:text-white transition-colors">About</a>
                            <a href="#" className="text-slate-600 hover:text-landing-primary dark:text-slate-500 dark:hover:text-white transition-colors">Legal</a>
                            <a href="#" className="text-slate-600 hover:text-landing-primary dark:text-slate-500 dark:hover:text-white transition-colors">Contact</a>
                        </div>
                    </div>
                </div>
                <div className="mx-auto max-w-[1200px] pt-8 mt-12 border-t border-slate-200 dark:border-landing-border text-center md:text-left text-xs text-slate-500 dark:text-slate-600">
                    © 2023 ExamPrep Inc. All rights reserved.
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
