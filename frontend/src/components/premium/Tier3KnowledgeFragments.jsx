import React from 'react'
import { Card, SectionHeader, MathText } from './ui'
import { Network, Search, Layers } from 'lucide-react'

/** Tier3 cards used under Knowledge / Graph (excludes Alternative Methods — those live under Step-by-Step). */
export const Tier3KnowledgeFragments = ({ data: t3 }) => {
    if (!t3) return null

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="p-6">
                    <SectionHeader title="Cross-Disciplinary Connections" icon={<Network className="w-5 h-5 text-purple-500" />} />
                    <div className="space-y-3">
                        {t3.connections_to_other_subjects &&
                            Object.entries(t3.connections_to_other_subjects || {}).map(([subject, desc], i) => (
                                <div key={i} className="flex gap-3 pb-3 border-b border-slate-100 last:border-0 last:pb-0">
                                    <div className="shrink-0 w-24">
                                        <span className="text-xs font-bold text-purple-700 bg-purple-100 px-2 py-1 rounded block text-center truncate">
                                            {subject}
                                        </span>
                                    </div>
                                    <p className="text-sm text-slate-700 text-xs leading-relaxed"><MathText>{desc}</MathText></p>
                                </div>
                            ))}
                    </div>
                </Card>

                <div className="space-y-6">
                    <Card className="p-6">
                        <SectionHeader title="Smart Search Keywords" icon={<Search className="w-5 h-5 text-blue-500" />} />
                        <div className="flex flex-wrap gap-2">
                            {(t3.search_keywords || []).map((kw, i) => (
                                <span key={i} className="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-full text-xs transition-colors cursor-default border border-slate-200">
                                    #{kw}
                                </span>
                            ))}
                        </div>
                    </Card>
                    <Card className="p-6">
                        <SectionHeader title="Deeper Dive Topics" icon={<Layers className="w-5 h-5 text-indigo-500" />} />
                        <ul className="list-disc pl-5 space-y-1">
                            {(t3.deeper_dive_topics || []).map((topic, i) => (
                                <li key={i} className="text-sm text-indigo-900 font-medium">{topic}</li>
                            ))}
                        </ul>
                    </Card>
                </div>
            </div>
        </div>
    )
}
