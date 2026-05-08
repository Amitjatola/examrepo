import React from 'react'
import { Card, SectionHeader, Badge, MathText } from './ui'
import { BookOpen, Video, GitBranch, Lightbulb, Factory, BarChart3, Waypoints } from 'lucide-react'

export const Tier1DifficultySection = ({ data: t1 }) => {
    if (!t1) return null
    return (
        <Card className="p-6">
            <SectionHeader title="Difficulty Deep Dive" icon={<BarChart3 className="w-5 h-5 text-slate-500" />} />
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                <div className="bg-slate-50 p-3 rounded-lg text-center">
                    <p className="text-xs text-slate-400 uppercase">Accuracy Exp.</p>
                    <p className="font-bold text-xl text-slate-700">{t1.difficulty_analysis?.expected_accuracy_percent || 'N/A'}%</p>
                </div>
                <div className="col-span-2 bg-slate-50 p-3 rounded-lg">
                    <p className="text-xs text-slate-400 uppercase mb-2">Complexity Breakdown</p>
                    <div className="flex gap-1 h-2 w-full rounded-full overflow-hidden mb-2">
                        <div className="bg-blue-400" style={{ flex: t1.difficulty_analysis?.complexity_breakdown?.conceptual || 1 }} title="Conceptual"></div>
                        <div className="bg-emerald-400" style={{ flex: t1.difficulty_analysis?.complexity_breakdown?.mathematical || 1 }} title="Mathematical"></div>
                        <div className="bg-amber-400" style={{ flex: t1.difficulty_analysis?.complexity_breakdown?.problem_solving || 1 }} title="Problem Solving"></div>
                    </div>
                    <div className="flex justify-between text-xs text-slate-500">
                        <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-blue-400"></div> Conc ({t1.difficulty_analysis?.complexity_breakdown?.conceptual || 0})</span>
                        <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-emerald-400"></div> Math ({t1.difficulty_analysis?.complexity_breakdown?.mathematical || 0})</span>
                        <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-amber-400"></div> Prob ({t1.difficulty_analysis?.complexity_breakdown?.problem_solving || 0})</span>
                    </div>
                </div>
            </div>
            <div>
                <h4 className="text-sm font-bold text-slate-800 mb-2">Difficulty Factors</h4>
                <ul className="list-disc space-y-2 pl-5 text-sm text-slate-700 dark:text-slate-300">
                    {(t1.difficulty_analysis?.difficulty_factors || []).map((factor, i) => (
                        <li key={i} className="min-w-0 max-w-full break-words [overflow-wrap:anywhere]">
                            <MathText inline>{factor}</MathText>
                        </li>
                    ))}
                </ul>
            </div>
        </Card>
    )
}

export const Tier1TextbookSection = ({ data: t1 }) => {
    if (!t1) return null
    return (
        <Card className="p-6">
            <SectionHeader title="Text Book Reference" icon={<BookOpen className="w-5 h-5 text-blue-500" />} />
            <div className="space-y-6">
                {(t1.textbook_references || []).map((ref, i) => (
                    <div key={i} className="text-sm border-b border-slate-100 last:border-0 pb-4 last:pb-0">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="font-bold text-slate-900 dark:text-white">{ref.book}</p>
                                <p className="text-slate-600 mb-1 text-xs">by {ref.author}</p>
                            </div>
                        </div>

                        <div className="flex flex-wrap gap-2 mb-2">
                            <Badge variant={ref.relevance_score > 0.9 ? 'green' : 'yellow'}>{((ref.relevance_score || 0) * 100).toFixed(0)}% Match</Badge>
                        </div>
                        <p className="text-xs text-slate-500"><span className="font-semibold">Section:</span> {ref.section}</p>
                        {ref.text_snippet && (
                            <blockquote className="mt-2 text-xs italic text-slate-600 bg-slate-50 p-3 rounded border-l-4 border-slate-300">
                                "{<MathText inline>{ref.text_snippet}</MathText>}"
                            </blockquote>
                        )}
                    </div>
                ))}
            </div>
        </Card>
    )
}

export const Tier1StepByStepSection = ({ data: t1 }) => {
    if (!t1) return null
    const rawSteps = Array.isArray(t1.explanation?.step_by_step)
        ? t1.explanation.step_by_step
        : []
    const normalizedPrimarySteps = rawSteps
        .map((step) => (step == null ? '' : String(step).trim()))
        .filter(Boolean)

    const parsedPathSteps = (t1.step_by_step_solution?.solution_path || '')
        .split(/\s*(?:->|→)\s*/g)
        .map((step) => step.trim())
        .filter(Boolean)

    const insightSteps = Array.isArray(t1.step_by_step_solution?.key_insights)
        ? t1.step_by_step_solution.key_insights
            .map((step) => (step == null ? '' : String(step).trim()))
            .filter(Boolean)
        : []

    const mergedFallbackSteps = [...parsedPathSteps, ...insightSteps]
    const expectedStepCount = Number(t1.step_by_step_solution?.total_steps) || 0

    const renderedSteps = [...normalizedPrimarySteps]
    const hasStep = new Set(renderedSteps.map((step) => step.toLowerCase()))

    if (renderedSteps.length < expectedStepCount) {
        for (const step of mergedFallbackSteps) {
            const stepKey = step.toLowerCase()
            if (hasStep.has(stepKey)) continue
            renderedSteps.push(step)
            hasStep.add(stepKey)
            if (renderedSteps.length >= expectedStepCount) break
        }
    }

    if (renderedSteps.length === 0) {
        renderedSteps.push(...mergedFallbackSteps)
    }

    return (
        <Card className="p-6">
            <SectionHeader title="Step-by-Step Explanation" icon={<Lightbulb className="w-5 h-5 text-amber-500" />} />

            <div className="mb-6 p-3 bg-amber-50 dark:bg-amber-950/35 border border-amber-100 dark:border-amber-900/50 rounded-lg flex flex-col sm:flex-row justify-between items-start sm:items-center text-sm gap-3">
                <div className="flex flex-wrap items-center gap-2 min-w-0">
                    <Waypoints className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
                    <span className="font-bold text-amber-800 dark:text-amber-200">Approach:</span>
                    <span className="text-amber-900 dark:text-amber-50">{t1.step_by_step_solution?.approach_type || 'N/A'}</span>
                </div>
                <div className="flex flex-wrap items-start gap-2 min-w-0 w-full sm:w-auto sm:max-w-[58%]">
                    <span className="font-bold text-amber-800 dark:text-amber-200 shrink-0">Path:</span>
                    <span className="text-amber-900 dark:text-amber-50 text-xs min-w-0 break-words leading-snug [&_.katex]:text-inherit">
                        <MathText inline>{t1.step_by_step_solution?.solution_path || 'N/A'}</MathText>
                    </span>
                </div>
            </div>

            <div className="space-y-4">
                {renderedSteps.map((step, idx) => (
                    <div key={idx} className="flex gap-4">
                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-slate-700 text-blue-700 dark:text-sky-300 flex items-center justify-center font-bold text-xs mt-0.5 border border-blue-200/80 dark:border-slate-600">
                            {idx + 1}
                        </div>
                        <div className="text-slate-700 dark:text-slate-100 leading-relaxed text-sm min-w-0 break-words [&_.katex]:text-inherit dark:[&_.katex]:text-slate-100">
                            <MathText>{step}</MathText>
                        </div>
                    </div>
                ))}
            </div>

            <div className="mt-6 pt-6 border-t border-slate-100 dark:border-slate-700">
                <p className="text-sm font-semibold text-slate-900 dark:text-white mb-3">Mathematical Principles:</p>
                <div className="overflow-x-auto">
                    <table className="min-w-full text-sm text-left table-fixed w-full">
                        <colgroup>
                            <col className="w-[22%]" />
                            <col className="w-[38%]" />
                            <col className="w-[40%]" />
                        </colgroup>
                        <thead className="bg-slate-50 dark:bg-slate-800/90 text-slate-600 dark:text-slate-300 font-medium">
                            <tr>
                                <th className="px-3 py-2 align-top">Name</th>
                                <th className="px-3 py-2 align-top">Formula</th>
                                <th className="px-3 py-2 align-top">Relevance</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                            {(t1.formulas_principles || []).map((fp, i) => (
                                <tr key={i}>
                                    <td className="px-3 py-2 font-medium text-slate-900 dark:text-gray-200 align-top min-w-0 break-words">{fp.name}</td>
                                    <td className="px-3 py-2 font-mono text-slate-900 dark:text-slate-100 bg-slate-100 dark:bg-slate-800/70 border-l border-slate-200/80 dark:border-slate-600/50 [&_.katex]:text-inherit align-top min-w-0 break-words overflow-x-auto">
                                        <MathText inline>{(fp.formula || "").toString().startsWith('$') ? fp.formula : '$' + fp.formula + '$'}</MathText>
                                    </td>
                                    <td className="px-3 py-2 text-xs text-slate-500 dark:text-slate-400 italic align-top min-w-0 whitespace-normal break-words leading-relaxed [&_.katex]:text-inherit dark:[&_.katex]:text-slate-400">
                                        {fp.relevance ? <MathText inline>{fp.relevance}</MathText> : null}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </Card>
    )
}

export const Tier1VideoSection = ({ data: t1 }) => {
    if (!t1) return null
    return (
        <Card className="p-6">
            <SectionHeader title="Video Lectures" icon={<Video className="w-5 h-5 text-red-500" />} />
            <div className="space-y-4">
                {(t1.video_references || []).map((ref, i) => (
                    <div key={i} className="text-sm bg-slate-50 p-3 rounded-lg border border-slate-100">
                        <div className="flex justify-between">
                            <p className="font-semibold text-slate-900 dark:text-white">{ref.topic_covered}</p>
                        </div>
                        <p className="text-xs text-slate-500 mb-2">{ref.professor}</p>
                        <div className="flex justify-between items-center mt-2">
                            <a href={ref.video_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-xs font-bold text-red-600 hover:text-red-700 uppercase tracking-wide">
                                <Video className="w-3 h-3" /> Watch ({ref.timestamp_start})
                            </a>
                        </div>
                    </div>
                ))}
            </div>
        </Card>
    )
}

export const Tier1RealWorldSection = ({ data: t1 }) => {
    if (!t1) return null
    return (
        <Card className="p-6 bg-gradient-to-br from-slate-800 to-slate-900 text-white border-0">
            <SectionHeader title="Real World Context" icon={<Factory className="w-5 h-5 text-emerald-400" />} />
            <div className="space-y-4 mt-2">
                <div>
                    <p className="text-xs font-bold text-slate-400 uppercase mb-1">Practical Relevance</p>
                    <p className="text-sm text-slate-200 leading-relaxed">
                        {t1.real_world_applications?.practical_relevance || 'N/A'}
                    </p>
                </div>
            </div>
        </Card>
    )
}

export const Tier1KnowledgeGraphSection = ({ data: t1 }) => {
    if (!t1) return null
    return (
        <Card className="p-6">
            <SectionHeader title="Knowledge Graph" icon={<GitBranch className="w-5 h-5 text-purple-500" />} />
            <div className="space-y-6">
                <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Dependency Tree</h4>
                    <div className="bg-slate-50 p-4 rounded-lg space-y-4 border border-slate-200">
                        {t1.prerequisites?.dependency_tree && Object.entries(t1.prerequisites.dependency_tree).map(([key, reqs]) => (
                            <div key={key}>
                                <p className="font-semibold text-slate-800 flex items-center gap-2 text-sm">
                                    <span className="w-2 h-2 rounded-full bg-purple-400"></span>
                                    {key}
                                </p>
                                <ul className="ml-2 mt-2 pl-3 border-l-2 border-slate-200 space-y-2">
                                    {(reqs || []).map((r, i) => (
                                        <li key={i} className="text-xs text-slate-600 flex items-center gap-2">
                                            <span className="px-1.5 py-0.5 rounded bg-slate-200 text-slate-600 font-mono text-[10px]">
                                                {r.includes('requires') ? 'REQ' : 'ENABLES'}
                                            </span>
                                            {r.replace(/(requires:|enables:)/, '').trim()}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </Card>
    )
}
