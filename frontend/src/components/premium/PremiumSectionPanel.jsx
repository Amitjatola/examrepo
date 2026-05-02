import React from 'react'
import {
    Tier1DifficultySection,
    Tier1TextbookSection,
    Tier1StepByStepSection,
    Tier1VideoSection,
    Tier1RealWorldSection,
    Tier1KnowledgeGraphSection,
} from './Tier1Sections'
import {
    CommonMistakesSection,
    ExamStrategyDetailSection,
    MnemonicsSection,
    FlashcardsSection,
    RealWorldSection,
} from './Tier2DeepDiveSections'
import { AlternativeMethodsSection } from './AlternativeMethodsSection'
import { Tier3KnowledgeFragments } from './Tier3KnowledgeFragments'
import { Tier4View } from './Tier4View'

/** @typedef {'difficulty'|'mistakes'|'exam_strategy'|'textbook'|'steps'|'alternative_tags'|'video'|'realworld'|'mnemonics'|'flashcards'|'knowledge'} PremiumSectionId */

/**
 * @param {{ question: any, section: PremiumSectionId }} props
 */
export const PremiumSectionPanel = ({ question, section }) => {
    const t1 = question?.tier_1_core_research
    const t2 = question?.tier_2_student_learning
    const t3 = question?.tier_3_enhanced_learning

    return (
        <div className="space-y-8">
            {section === 'difficulty' && (t1 ? <Tier1DifficultySection data={t1} /> : null)}

            {section === 'mistakes' && <CommonMistakesSection mistakes={t2?.common_mistakes} />}

            {section === 'exam_strategy' && <ExamStrategyDetailSection examStrategy={t2?.exam_strategy} />}

            {section === 'textbook' && t1 ? <Tier1TextbookSection data={t1} /> : null}

            {section === 'steps' && (t1 ? <Tier1StepByStepSection data={t1} /> : null)}

            {section === 'alternative_tags' && (
                <AlternativeMethodsSection alternativeMethods={t3?.alternative_methods} defaultOpen />
            )}

            {section === 'video' && t1 ? <Tier1VideoSection data={t1} /> : null}

            {section === 'realworld' && (
                <div className="space-y-6">
                    {t1?.real_world_applications?.practical_relevance &&
                    String(t1.real_world_applications.practical_relevance).trim() !== '' &&
                    t1.real_world_applications.practical_relevance !== 'N/A' ? (
                        <Tier1RealWorldSection data={t1} />
                    ) : null}
                    <RealWorldSection contexts={t2?.real_world_context || []} />
                </div>
            )}

            {section === 'mnemonics' && <MnemonicsSection mnemonics={t2?.mnemonics_memory_aids || []} />}

            {section === 'flashcards' && <FlashcardsSection flashcards={t2?.flashcards || []} />}

            {section === 'knowledge' && (
                <div className="space-y-8">
                    {t1 ? <Tier1KnowledgeGraphSection data={t1} /> : null}
                    <Tier3KnowledgeFragments data={t3} />
                    {question?.tier_4_metadata_and_future ? <Tier4View data={question} /> : null}
                </div>
            )}
        </div>
    )
}
