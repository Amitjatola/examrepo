import React from 'react'
import {
    CommonMistakesSection,
    ExamStrategyDetailSection,
    MnemonicsSection,
    FlashcardsSection,
    RealWorldSection,
} from './Tier2DeepDiveSections'

export const Tier2View = ({ data }) => {
    if (!data) return null
    const t2 = data
    const mistakes = t2.common_mistakes || []
    const mnemonics = t2.mnemonics_memory_aids || []
    const flashcards = t2.flashcards || []
    const realWorld = t2.real_world_context || []

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
                <CommonMistakesSection mistakes={mistakes} />
                <ExamStrategyDetailSection examStrategy={t2.exam_strategy} />
            </div>
            <div className="space-y-6">
                <MnemonicsSection mnemonics={mnemonics} />
                <FlashcardsSection flashcards={flashcards} />
                <RealWorldSection contexts={realWorld} />
            </div>
        </div>
    )
}
