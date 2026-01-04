import React, { useState } from 'react';
import { Tier0View } from './Tier0View';
import { Tier1View } from './Tier1View';
import { Tier2View } from './Tier2View';
import { Tier3View } from './Tier3View';
import { Tier4View } from './Tier4View';
import { Activity, Brain, Lightbulb, Globe, Database, Lock } from 'lucide-react';
import { Card } from './ui';
import { useAuth } from '../../context/AuthContext';

export const TierViews = ({ question, isPremium = false }) => {
    const [activeTier, setActiveTier] = useState(1); // Default to Research (Tier 1)
    const { user, subscription, openLogin } = useAuth();

    // Check if we have data for each tier to potentially disable tabs
    const hasData = (tier) => {
        if (!question) return false;
        switch (tier) {
            case 0: return !!question.tier_0_classification;
            case 1: return !!question.tier_1_core_research;
            case 2: return !!question.tier_2_student_learning;
            case 3: return !!question.tier_3_enhanced_learning;
            case 4: return !!question.tier_4_metadata; // Changed from metadata_and_future to metadata to match schema
            default: return false;
        }
    };

    const tabs = [
        { id: 0, label: 'Classification', icon: Activity, color: 'text-blue-500' },
        { id: 1, label: 'Core Research', icon: Brain, color: 'text-emerald-500' },
        { id: 2, label: 'Student Zone', icon: Lightbulb, color: 'text-amber-500' },
        { id: 3, label: 'Deep Dive', icon: Globe, color: 'text-purple-500' },
        { id: 4, label: 'System Meta', icon: Database, color: 'text-slate-500' },
    ];

    if (!isPremium) {
        // Determine message based on user and subscription status
        let message = "Sign in to unlock deep insights, step-by-step derivations, and AI-powered learning aids.";
        let buttonText = "Sign In to Continue";
        let buttonAction = openLogin;
        let showTrialInfo = false;
        let trialDays = 0;

        if (user && subscription) {
            if (subscription.subscription_type === 'trial' && subscription.status === 'expired') {
                message = "Your 7-day free trial has expired. Upgrade to Premium to continue accessing advanced analytics.";
                buttonText = "Upgrade to Premium";
                buttonAction = () => console.log("Redirect to pricing"); // TODO: Implement pricing page
            } else if (subscription.subscription_type === 'free') {
                message = "Unlock deep insights, step-by-step derivations, and AI-powered learning aids with Premium.";
                buttonText = "Upgrade to Premium";
                buttonAction = () => console.log("Redirect to pricing");
            }
        }

        return (
            <Card className="p-8 text-center bg-slate-50 dark:bg-slate-900/50 mt-8">
                <Lock className="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Premium Analytics</h3>
                <p className="text-slate-600 dark:text-gray-400 mb-6">{message}</p>
                <button
                    onClick={buttonAction}
                    className={`${!user
                        ? 'bg-primary hover:bg-blue-600'
                        : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700'
                        } text-white px-6 py-2 rounded-lg transition-colors`}
                >
                    {buttonText}
                </button>
            </Card>
        );
    }

    if (!hasData(1)) return null; // If no core research, probably no premium data at all

    return (
        <div className="mt-8">
            <div className="flex flex-wrap gap-2 mb-6 border-b border-slate-200 pb-1">
                {tabs.map((tab) => {
                    const isActive = activeTier === tab.id;
                    const available = hasData(tab.id);
                    const Icon = tab.icon;

                    if (!available) return null;

                    return (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTier(tab.id)}
                            className={`flex items-center gap-2 px-4 py-3 rounded-t-lg transition-all border-b-2 ${isActive
                                ? 'bg-white border-brand-500 text-brand-700 shadow-sm'
                                : 'bg-transparent border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-50'
                                }`}
                        >
                            <Icon className={`w-4 h-4 ${isActive ? tab.color : 'text-slate-400'}`} />
                            <span className="font-medium text-sm">{tab.label}</span>
                        </button>
                    );
                })}
            </div>

            <div className="min-h-[400px]">
                {activeTier === 0 && <Tier0View data={question.tier_0_classification} />}
                {activeTier === 1 && <Tier1View data={question.tier_1_core_research} />}
                {activeTier === 2 && <Tier2View data={question.tier_2_student_learning} />}
                {activeTier === 3 && <Tier3View data={question.tier_3_enhanced_learning} />}
                {activeTier === 4 && <Tier4View data={question} />}
            </div>
        </div>
    );
};
