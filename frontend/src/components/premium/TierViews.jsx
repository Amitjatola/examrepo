import React, { useState, useEffect } from 'react'
import {
    BarChart3,
    BookOpen,
    ListOrdered,
    Video,
    Globe,
    GitBranch,
    Lock,
    AlertTriangle,
    Target,
    Brain,
    Layers,
    Tags,
} from 'lucide-react'
import { Card } from './ui'
import { useAuth } from '../../context/AuthContext'
import { PremiumSectionPanel } from './PremiumSectionPanel'

/** Tab order: Tier1 difficulty, then Tier2 student blocks, then remaining Tier1 tabs, Knowledge last */
const SECTION_ORDER = [
    'difficulty',
    'mistakes',
    'exam_strategy',
    'textbook',
    'steps',
    'alternative_tags',
    'video',
    'realworld',
    'mnemonics',
    'flashcards',
    'knowledge',
]

/** @param {string} sectionId @param {any} q */
export const sectionHasData = (sectionId, q) => {
    const t1 = q?.tier_1_core_research
    const t2 = q?.tier_2_student_learning
    const t3 = q?.tier_3_enhanced_learning
    const t4 = q?.tier_4_metadata_and_future

    switch (sectionId) {
        case 'difficulty': {
            const da = t1?.difficulty_analysis
            const breakdown = da?.complexity_breakdown
            const hasBreakdownValues =
                breakdown != null &&
                typeof breakdown === 'object' &&
                Object.values(breakdown).some((v) => v != null && Number(v) !== 0)
            const hasT1 =
                da != null &&
                (da.expected_accuracy_percent != null || hasBreakdownValues || (da.difficulty_factors || []).length > 0)
            return Boolean(hasT1)
        }
        case 'mistakes':
            return (t2?.common_mistakes || []).length > 0
        case 'exam_strategy':
            return (
                t2?.exam_strategy != null &&
                typeof t2.exam_strategy === 'object' &&
                Object.keys(t2.exam_strategy || {}).length > 0
            )
        case 'textbook':
            return (t1?.textbook_references || []).length > 0
        case 'steps': {
            const steps = t1?.explanation?.step_by_step
            const fp = t1?.formulas_principles
            const sbs = t1?.step_by_step_solution
            const hasT1 =
                (steps || []).length > 0 ||
                (fp || []).length > 0 ||
                Boolean(sbs && (sbs.approach_type || sbs.solution_path))
            return Boolean(hasT1)
        }
        case 'alternative_tags': {
            const alt = t3?.alternative_methods
            return Array.isArray(alt) && alt.length > 0
        }
        case 'video':
            return (t1?.video_references || []).length > 0
        case 'realworld': {
            const pr = t1?.real_world_applications?.practical_relevance
            const hasT1 = typeof pr === 'string' && pr.trim().length > 0 && pr !== 'N/A'
            const hasContexts = (t2?.real_world_context || []).length > 0
            return hasT1 || hasContexts
        }
        case 'mnemonics':
            return (t2?.mnemonics_memory_aids || []).length > 0
        case 'flashcards':
            return (t2?.flashcards || []).length > 0
        case 'knowledge': {
            const tree = t1?.prerequisites?.dependency_tree
            const hasTree = tree != null && typeof tree === 'object' && Object.keys(tree).length > 0
            const conn = t3?.connections_to_other_subjects
            const hasConn = conn != null && typeof conn === 'object' && Object.keys(conn).length > 0
            const hasKw = (t3?.search_keywords || []).length > 0
            const hasDive = (t3?.deeper_dive_topics || []).length > 0
            return Boolean(hasTree || hasConn || hasKw || hasDive || !!t4)
        }
        default:
            return false
    }
}

const pickDefaultSection = (q) => {
    for (const id of SECTION_ORDER) {
        if (sectionHasData(id, q)) return id
    }
    return 'difficulty'
}

const TABS = [
    { id: 'difficulty', line1: 'Difficulty', line2: 'Deep Dive', icon: BarChart3, color: 'text-emerald-500' },
    { id: 'mistakes', line1: 'Common Mistakes', line2: '& Traps', icon: AlertTriangle, color: 'text-emerald-500' },
    { id: 'exam_strategy', line1: 'Exam', line2: 'Strategy', icon: Target, color: 'text-emerald-500' },
    { id: 'textbook', line1: 'Textbook', line2: 'Reference', icon: BookOpen, color: 'text-emerald-500' },
    { id: 'steps', line1: 'Step-by-Step', line2: 'Explanation', icon: ListOrdered, color: 'text-emerald-500' },
    { id: 'alternative_tags', line1: 'Alternative tags', line2: 'Compare approaches', icon: Tags, color: 'text-emerald-500' },
    { id: 'video', line1: 'Video', line2: 'Lectures', icon: Video, color: 'text-emerald-500' },
    { id: 'realworld', line1: 'Real World', line2: 'Context', icon: Globe, color: 'text-emerald-500' },
    { id: 'mnemonics', line1: 'Mnemonics', line2: '& Memory Aids', icon: Brain, color: 'text-emerald-500' },
    { id: 'flashcards', line1: 'Flashcards', line2: 'Study', icon: Layers, color: 'text-emerald-500' },
    { id: 'knowledge', line1: 'Knowledge', line2: 'Graph', icon: GitBranch, color: 'text-emerald-500' },
]

export const TierViews = ({ question }) => {
    const [activeSection, setActiveSection] = useState('difficulty')
    const { user, subscription, openLogin, isPremium, isLoading, fetchSubscription } = useAuth()

    const hasTier1 = Boolean(question?.tier_1_core_research)

    useEffect(() => {
        if (!question) return
        const next = pickDefaultSection(question)
        setActiveSection(next)
    }, [question?.id])

    if (!isPremium) {
        if (isLoading) {
            return (
                <Card className="p-8 text-center bg-slate-50 dark:bg-slate-900/50">
                    <Lock className="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-4 animate-pulse" />
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Premium Analytics</h3>
                    <p className="text-slate-600 dark:text-gray-400 mb-0">Loading subscription…</p>
                </Card>
            )
        }

        let message = "Sign in to unlock deep insights, step-by-step derivations, and AI-powered learning aids."
        let buttonText = "Sign In to Continue"
        let buttonAction = openLogin

        if (user && !subscription) {
            message = "Could not verify your subscription. Check your connection or API URL, then try again."
            buttonText = "Retry"
            buttonAction = () => {
                fetchSubscription()
            }
        } else if (user && subscription) {
            if (subscription.subscription_type === 'trial' && subscription.status === 'expired') {
                message = "Your 7-day free trial has expired. Upgrade to Premium to continue accessing advanced analytics."
                buttonText = "Upgrade to Premium"
                buttonAction = () => console.log("Redirect to pricing")
            } else if (subscription.subscription_type === 'free') {
                message = "Unlock deep insights, step-by-step derivations, and AI-powered learning aids with Premium."
                buttonText = "Upgrade to Premium"
                buttonAction = () => console.log("Redirect to pricing")
            }
        }

        return (
            <Card className="p-8 text-center bg-slate-50 dark:bg-slate-900/50">
                <Lock className="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Premium Analytics</h3>
                <p className="text-slate-600 dark:text-gray-400 mb-6">{message}</p>
                <button
                    type="button"
                    onClick={buttonAction}
                    className={`${!user
                        ? 'bg-primary hover:bg-blue-600'
                        : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700'
                        } text-white px-6 py-2 rounded-lg transition-colors`}
                >
                    {buttonText}
                </button>
            </Card>
        )
    }

    if (!hasTier1) return null

    return (
        <div>
            <div className="flex flex-wrap gap-2 mb-4 border-b border-slate-200 dark:border-white/10 pb-1">
                {TABS.map((tab) => {
                    const isActive = activeSection === tab.id
                    const available = sectionHasData(tab.id, question)
                    const Icon = tab.icon

                    if (!available) return null

                    return (
                        <button
                            key={tab.id}
                            type="button"
                            onClick={() => setActiveSection(tab.id)}
                            className={`flex items-center gap-2 px-3 sm:px-4 py-2.5 sm:py-3 rounded-t-lg transition-all border-b-2 text-left ${isActive
                                ? 'bg-white dark:bg-white/10 border-brand-500 text-brand-700 dark:text-white shadow-sm'
                                : 'bg-transparent border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-white/5'
                                }`}
                        >
                            <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? tab.color : 'text-slate-400 dark:text-slate-500'}`} />
                            <span className="flex flex-col items-start leading-tight min-w-0">
                                <span className="font-medium text-sm">{tab.line1}</span>
                                <span className="text-xs text-slate-500 dark:text-slate-400 font-normal">{tab.line2}</span>
                            </span>
                        </button>
                    )
                })}
            </div>

            <PremiumSectionPanel question={question} section={activeSection} />
        </div>
    )
}
