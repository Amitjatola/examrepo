import React from 'react';
import { Check, Zap, BarChart, BookOpen, Crown, ArrowRight, ArrowLeft } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const PremiumPage = ({ onBack }) => {
    const { isPremium, openLogin, user } = useAuth();

    const handleHeroCta = () => {
        if (isPremium || user) return;
        openLogin();
    };

    const handleUpgradeCta = () => {
        if (isPremium || user) return;
        openLogin();
    };

    return (
        <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-background-dark h-full">
            <div className="max-w-5xl mx-auto px-6 py-12 space-y-16">
                {typeof onBack === 'function' && (
                    <button
                        type="button"
                        onClick={onBack}
                        className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 dark:text-slate-300 hover:text-primary transition-colors -mt-4 mb-2"
                        aria-label="Back to app"
                    >
                        <ArrowLeft size={18} aria-hidden />
                        Back to app
                    </button>
                )}

                {isPremium && (
                    <div
                        className="rounded-xl border border-emerald-200 dark:border-emerald-800/50 bg-emerald-50 dark:bg-emerald-900/20 px-4 py-3 text-emerald-900 dark:text-emerald-100 text-sm font-medium"
                        role="status"
                    >
                        You have Pro access. All premium features are unlocked on this account.
                    </div>
                )}

                {/* Hero Section */}
                <div className="space-y-6">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 text-xs font-bold uppercase tracking-wider">
                        <Zap size={14} fill="currentColor" />
                        <span>Limited Time Offer</span>
                    </div>

                    <h1
                        data-testid="premium-hero-title"
                        className="text-4xl md:text-5xl font-display font-bold text-slate-900 dark:text-white leading-tight"
                    >
                        Unlock your full potential
                    </h1>

                    <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl leading-relaxed">
                        Start your 7-day free trial today. Pro unlocks full step-by-step solutions, all hint steps, tiered research insights, quick revision (mnemonics & flashcards), and trap-style question filters—on top of everything in Basic.
                    </p>

                    {!isPremium && (
                        <>
                            <div className="flex flex-col sm:flex-row gap-4 pt-4">
                                <button
                                    type="button"
                                    onClick={handleHeroCta}
                                    disabled={Boolean(user)}
                                    className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-primary hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-bold text-lg transition-all shadow-lg hover:shadow-primary/25 active:scale-95"
                                >
                                    <span>Start 7-Day Free Trial</span>
                                    <ArrowRight size={20} aria-hidden />
                                </button>
                            </div>
                            <p className="text-xs text-slate-400 mt-2 text-left sm:text-left pl-2">
                                {user ? 'Signed in — use the plan below when checkout is connected.' : 'No credit card required for trial'}
                            </p>
                        </>
                    )}
                </div>

                {/* Benefits Grid */}
                <div>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-8">Premium Benefits</h2>
                    <div className="grid md:grid-cols-3 gap-6">
                        {/* Benefit 1 */}
                        <div className="bg-white dark:bg-card-dark p-8 rounded-2xl border border-slate-200 dark:border-border-dark shadow-sm hover:shadow-xl transition-shadow duration-300">
                            <div className="w-12 h-12 bg-blue-50 dark:bg-blue-900/20 rounded-xl flex items-center justify-center text-primary mb-6">
                                <BookOpen size={24} />
                            </div>
                            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Full solutions & hints</h3>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                                Every step-by-step derivation, unlimited progressive hints per question, and higher daily solution unlocks than Basic.
                            </p>
                        </div>

                        {/* Benefit 2 */}
                        <div className="bg-white dark:bg-card-dark p-8 rounded-2xl border border-slate-200 dark:border-border-dark shadow-sm hover:shadow-xl transition-shadow duration-300">
                            <div className="w-12 h-12 bg-indigo-50 dark:bg-indigo-900/20 rounded-xl flex items-center justify-center text-indigo-600 mb-6">
                                <BarChart size={24} />
                            </div>
                            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Smart search & traps</h3>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                                Filter the bank by complexity flags (edge cases, ambiguous wording, multi-step). Pair with your topic heatmap for targeted drills.
                            </p>
                        </div>

                        {/* Benefit 3 */}
                        <div className="bg-white dark:bg-card-dark p-8 rounded-2xl border border-slate-200 dark:border-border-dark shadow-sm hover:shadow-xl transition-shadow duration-300">
                            <div className="w-12 h-12 bg-amber-50 dark:bg-amber-900/20 rounded-xl flex items-center justify-center text-amber-600 mb-6">
                                <Crown size={24} />
                            </div>
                            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Tier insights & revision</h3>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                                Unlock classification, research tiers, mnemonics, flashcards, and a quick revision panel on every question.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Pricing Section */}
                <div className="flex justify-center pb-12 w-full">
                    {/* Toggle Switch */}
                    <div className="flex items-center justify-center w-full max-w-4xl mb-6 gap-4">
                        <span className="text-sm font-bold text-slate-500 dark:text-slate-400">Monthly</span>
                        <div className="flex items-center gap-2 p-1.5 bg-slate-100 dark:bg-white/5 rounded-2xl border border-slate-200 dark:border-white/10">
                            <div className="px-4 py-2 rounded-xl bg-white dark:bg-slate-800 shadow-sm text-sm font-bold text-slate-900 dark:text-white">Annual</div>
                            <div className="px-3 py-1 rounded-full bg-green-500 text-[10px] font-black text-white uppercase tracking-wider animate-pulse">-35% SAVE</div>
                        </div>
                        <span className="text-sm font-medium text-slate-400">Lifetime</span>
                    </div>
                </div>

                <div className="flex justify-center pb-12 -mt-16">
                    <div className="w-full max-w-4xl grid md:grid-cols-2 gap-8 items-stretch">
                        {/* Free Plan */}
                        <div className="p-8 rounded-3xl border border-slate-200 dark:border-border-dark bg-white/50 dark:bg-card-dark/30 flex flex-col h-full">
                            <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">Basic</h3>
                            <h2 className="text-4xl font-extrabold text-slate-900 dark:text-white mb-4">Free</h2>
                            <p className="text-slate-500 dark:text-slate-400 mb-8">Everything you need to start practicing.</p>

                            <ul className="space-y-4 mb-8 flex-1">
                                <li className="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                                    <Check size={18} className="text-green-500" />
                                    <span>Unlimited practice questions</span>
                                </li>
                                <li className="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                                    <Check size={18} className="text-green-500" />
                                    <span>All papers (2007–2024)</span>
                                </li>
                                <li className="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                                    <Check size={18} className="text-green-500" />
                                    <span>Full search & community discussions</span>
                                </li>
                            </ul>
                        </div>

                        {/* Premium Plan */}
                        <div className="relative p-10 rounded-[2.5rem] border-2 border-primary bg-white dark:bg-[#15192b] shadow-[0_0_50px_-12px_rgba(56,88,250,0.3)] dark:shadow-[0_0_50px_-12px_rgba(56,88,250,0.2)] overflow-hidden flex flex-col h-full transform transition-transform hover:scale-[1.02] duration-300">
                            <div className="absolute top-0 right-0 bg-primary text-white text-[10px] font-black px-6 py-2 rounded-bl-3xl uppercase tracking-[0.2em] shadow-lg">
                                Popular
                            </div>

                            <h3 className="text-xl font-black text-primary mb-3 uppercase tracking-widest">Pro Access</h3>
                            <div className="flex items-baseline gap-1 mb-2">
                                <div className="text-6xl font-black text-slate-900 dark:text-white tracking-tighter">$19</div>
                                <div className="text-slate-400 font-bold text-lg">/mo</div>
                            </div>
                            <p className="text-sm text-slate-500 dark:text-slate-400 mb-10 font-medium">Everything you need to master GATE.</p>

                            <ul className="space-y-5 mb-12 flex-1">
                                <li className="flex items-center gap-4 text-slate-900 dark:text-white font-bold">
                                    <div className="size-6 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0"><Check size={14} strokeWidth={4} /></div>
                                    <span className="text-sm">Full Step-by-Step Solutions</span>
                                </li>
                                <li className="flex items-center gap-4 text-slate-900 dark:text-white font-bold">
                                    <div className="size-6 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0"><Check size={14} strokeWidth={4} /></div>
                                    <span className="text-sm">AI Performance Analytics</span>
                                </li>
                                <li className="flex items-center gap-4 text-slate-900 dark:text-white font-bold">
                                    <div className="size-6 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0"><Check size={14} strokeWidth={4} /></div>
                                    <span className="text-sm">Topic Research Insights</span>
                                </li>
                                <li className="flex items-center gap-4 text-slate-900 dark:text-white font-bold">
                                    <div className="size-6 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0"><Check size={14} strokeWidth={4} /></div>
                                    <span className="text-sm">Trap / complexity filters + all hint steps</span>
                                </li>
                            </ul>

                            <button
                                type="button"
                                onClick={handleUpgradeCta}
                                disabled={isPremium || Boolean(user)}
                                className="w-full py-5 bg-primary hover:bg-blue-600 disabled:hover:bg-primary disabled:opacity-70 disabled:cursor-not-allowed text-white rounded-2xl font-black text-lg transition-all shadow-xl shadow-primary/30 transform active:scale-95 group relative overflow-hidden"
                            >
                                <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
                                <span className="relative z-10">
                                    {isPremium ? 'Current plan: Pro' : user ? 'Checkout coming soon' : 'Get Full Access'}
                                </span>
                            </button>
                            {user && !isPremium && (
                                <p className="text-center text-xs text-slate-500 dark:text-slate-400 mt-3">
                                    Signed in as {user.email}. Payment integration can replace this button when you connect billing.
                                </p>
                            )}
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default PremiumPage;
