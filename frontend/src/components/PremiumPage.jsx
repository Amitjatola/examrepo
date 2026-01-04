import React from 'react';
import { Check, Zap, BarChart, BookOpen, Crown, ArrowRight } from 'lucide-react';

const PremiumPage = () => {
    return (
        <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-background-dark h-full">
            <div className="max-w-5xl mx-auto px-6 py-12 space-y-16">

                {/* Hero Section */}
                <div className="space-y-6">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 text-xs font-bold uppercase tracking-wider">
                        <Zap size={14} fill="currentColor" />
                        <span>Limited Time Offer</span>
                    </div>

                    <h1 className="text-4xl md:text-5xl font-display font-bold text-slate-900 dark:text-white leading-tight">
                        Unlock your full potential
                    </h1>

                    <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl leading-relaxed">
                        Start your 7-day free trial today. Master your exam with unlimited access to premium content, advanced analytics, and AI-powered study plans.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 pt-4">
                        <button className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-primary hover:bg-blue-700 text-white rounded-xl font-bold text-lg transition-all shadow-lg hover:shadow-primary/25 active:scale-95">
                            <span>Start 7-Day Free Trial</span>
                            <ArrowRight size={20} />
                        </button>
                    </div>
                    <p className="text-xs text-slate-400 mt-2 text-left sm:text-left pl-2">No credit card required for trial</p>
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
                            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Unlimited Practice</h3>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                                Access 5,000+ questions without daily limits. Generate custom quizzes based on your weak areas.
                            </p>
                        </div>

                        {/* Benefit 2 */}
                        <div className="bg-white dark:bg-card-dark p-8 rounded-2xl border border-slate-200 dark:border-border-dark shadow-sm hover:shadow-xl transition-shadow duration-300">
                            <div className="w-12 h-12 bg-indigo-50 dark:bg-indigo-900/20 rounded-xl flex items-center justify-center text-indigo-600 mb-6">
                                <BarChart size={24} />
                            </div>
                            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Advanced Analytics</h3>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                                Visualize your progress with detailed heatmaps. Understand exactly where to focus your study time.
                            </p>
                        </div>

                        {/* Benefit 3 */}
                        <div className="bg-white dark:bg-card-dark p-8 rounded-2xl border border-slate-200 dark:border-border-dark shadow-sm hover:shadow-xl transition-shadow duration-300">
                            <div className="w-12 h-12 bg-amber-50 dark:bg-amber-900/20 rounded-xl flex items-center justify-center text-amber-600 mb-6">
                                <Crown size={24} />
                            </div>
                            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Premium Content</h3>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                                Exclusive video walkthroughs for hard problems and expert tips from top scorers.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Pricing Section */}
                <div className="flex justify-center pb-12 w-full">
                    {/* Toggle Switch (Visual only for now) */}
                    <div className="flex items-center justify-end w-full max-w-4xl mb-6 gap-3">
                        <span className="text-sm font-medium text-slate-500">Monthly</span>
                        <span className="px-3 py-1 rounded-lg bg-white border border-slate-200 text-sm font-bold text-slate-900 shadow-sm">Annual <span className="text-green-600">-35%</span></span>
                    </div>
                </div>

                <div className="flex justify-center pb-12 -mt-16">
                    <div className="w-full max-w-4xl grid md:grid-cols-2 gap-8 items-stretch">
                        {/* Free Plan */}
                        <div className="p-8 rounded-3xl border border-slate-200 dark:border-border-dark bg-white/50 dark:bg-card-dark/30 flex flex-col h-full">
                            <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">Basic</h3>
                            <h2 className="text-4xl font-extrabold text-slate-900 dark:text-white mb-4">Free</h2>
                            <p className="text-slate-500 dark:text-slate-400 mb-8">Forever free plan for casual study.</p>

                            <ul className="space-y-4 mb-8 flex-1">
                                <li className="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                                    <Check size={18} className="text-green-500" />
                                    <span>20 Practice questions / day</span>
                                </li>
                                <li className="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                                    <Check size={18} className="text-green-500" />
                                    <span>Basic score tracking</span>
                                </li>
                                <li className="flex items-center gap-3 text-slate-400">
                                    <div className="p-0.5"><Check size={12} className="opacity-0" /></div>
                                    <span className="line-through opacity-70">No detailed analytics</span>
                                </li>
                            </ul>
                        </div>

                        {/* Premium Plan */}
                        <div className="relative p-8 rounded-3xl border-2 border-primary bg-white dark:bg-card-dark shadow-2xl overflow-hidden flex flex-col h-full">
                            <div className="absolute top-0 right-0 bg-primary text-white text-xs font-bold px-4 py-1.5 rounded-bl-xl uppercase tracking-wide">
                                Most Popular
                            </div>

                            <h3 className="text-lg font-bold text-primary mb-2">Premium</h3>
                            <div className="flex items-baseline gap-1 mb-2">
                                <div className="text-5xl font-extrabold text-slate-900 dark:text-white">$19</div>
                                <div className="text-slate-500 font-medium">/mo</div>
                            </div>
                            <p className="text-sm text-slate-500 dark:text-slate-400 mb-8">Billed annually ($228/year)</p>

                            <ul className="space-y-4 mb-8 flex-1">
                                <li className="flex items-center gap-3 text-slate-900 dark:text-white font-medium">
                                    <div className="p-0.5 rounded-full bg-primary text-white"><Check size={12} strokeWidth={3} /></div>
                                    <span>Unlimited Practice questions</span>
                                </li>
                                <li className="flex items-center gap-3 text-slate-900 dark:text-white font-medium">
                                    <div className="p-0.5 rounded-full bg-primary text-white"><Check size={12} strokeWidth={3} /></div>
                                    <span>Advanced Analytics & Heatmaps</span>
                                </li>
                                <li className="flex items-center gap-3 text-slate-900 dark:text-white font-medium">
                                    <div className="p-0.5 rounded-full bg-primary text-white"><Check size={12} strokeWidth={3} /></div>
                                    <span>Premium Video Solutions</span>
                                </li>
                            </ul>

                            <button className="w-full py-4 bg-primary hover:bg-blue-700 text-white rounded-xl font-bold transition-colors shadow-lg shadow-primary/20">
                                Start 7-Day Free Trial
                            </button>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default PremiumPage;
