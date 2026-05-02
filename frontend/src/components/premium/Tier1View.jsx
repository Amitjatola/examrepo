import React from 'react'
import {
    Tier1DifficultySection,
    Tier1TextbookSection,
    Tier1StepByStepSection,
    Tier1VideoSection,
    Tier1RealWorldSection,
    Tier1KnowledgeGraphSection,
} from './Tier1Sections'

/** Full Tier1 scroll view (legacy): all six sections stacked. Prefer {@link PremiumSectionPanel} + section tabs for app shell. */
export const Tier1View = ({ data }) => {
    if (!data) return null

    return (
        <div className="space-y-8">
            <div className="space-y-8">
                <Tier1DifficultySection data={data} />
                <Tier1TextbookSection data={data} />
                <Tier1StepByStepSection data={data} />
                <Tier1VideoSection data={data} />
                <Tier1RealWorldSection data={data} />
                <Tier1KnowledgeGraphSection data={data} />
            </div>
        </div>
    )
}
