import React from 'react'
import { AlternativeMethodsSection } from './AlternativeMethodsSection'
import { Tier3KnowledgeFragments } from './Tier3KnowledgeFragments'

export const Tier3View = ({ data }) => {
    if (!data) return null
    const t3 = data

    return (
        <div className="space-y-6">
            <Tier3KnowledgeFragments data={t3} />
            <AlternativeMethodsSection alternativeMethods={t3.alternative_methods} defaultOpen />
        </div>
    )
}
