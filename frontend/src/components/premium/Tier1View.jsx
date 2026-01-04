import React from 'react';
import { Card, SectionHeader, Badge, MathText } from './ui';
import { BookOpen, Video, GitBranch, Lightbulb, Factory, Puzzle, BarChart3, Waypoints, CheckCircle, Clock } from 'lucide-react';

export const Tier1View = ({ data }) => {
    if (!data) return null;
    const t1 = data;

    return (
        <div className="space-y-8">
            {/* Answer Validation & Time Metadata */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="p-4 bg-emerald-50 border-emerald-100 flex items-center justify-between">
                    <div>
                        <p className="text-xs font-bold text-emerald-800 uppercase">AI Confidence</p>
                        <div className="flex items-center gap-2">
                            <CheckCircle className="w-4 h-4 text-emerald-600" />
                            <span className="font-mono font-bold text-emerald-900">{(t1.answer_validation.confidence * 100).toFixed(0)}%</span>
                        </div>
                        <p className="text-[10px] text-emerald-600 mt-1">Type: {t1.answer_validation.confidence_type}</p>
                    </div>
                </Card>
                <Card className="p-4 bg-blue-50 border-blue-100 flex items-center justify-between">
                    <div>
                        <p className="text-xs font-bold text-blue-800 uppercase">Read Time</p>
                        <div className="flex items-center gap-2">
                            <Clock className="w-4 h-4 text-blue-600" />
                            <span className="font-mono font-bold text-blue-900">{t1.explanation.estimated_time_minutes} min</span>
                        </div>
                        <p className="text-[10px] text-blue-600 mt-1">Explanation Review</p>
                    </div>
                </Card>
                <Card className="p-4 bg-purple-50 border-purple-100 flex items-center justify-between">
                    <div>
                        <p className="text-xs font-bold text-purple-800 uppercase">Subject Conf.</p>
                        <div className="flex items-center gap-2">
                            <Puzzle className="w-4 h-4 text-purple-600" />
                            <span className="font-mono font-bold text-purple-900">{(t1.hierarchical_tags.subject.confidence * 100).toFixed(0)}%</span>
                        </div>
                        <p className="text-[10px] text-purple-600 mt-1">{t1.hierarchical_tags.subject.name}</p>
                    </div>
                </Card>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
                <Card className="p-4 flex-1 bg-gradient-to-r from-blue-50 to-white">
                    <div className="flex items-center gap-2 mb-2">
                        <Puzzle className="w-4 h-4 text-blue-500" />
                        <span className="text-xs font-bold text-blue-900 uppercase">Question Nature</span>
                    </div>
                    <p className="font-semibold text-lg text-slate-900 dark:text-white">{t1.explanation.question_nature}</p>
                </Card>
                <Card className="p-4 flex-1 bg-gradient-to-r from-purple-50 to-white">
                    <div className="flex items-center gap-2 mb-2">
                        <BookOpen className="w-4 h-4 text-purple-500" />
                        <span className="text-xs font-bold text-purple-900 uppercase">Syllabus Topic</span>
                    </div>
                    <p className="font-semibold text-sm text-slate-900 dark:text-white">{t1.hierarchical_tags.topic.name}</p>
                    <p className="text-xs text-slate-500 mt-1 font-mono">{t1.hierarchical_tags.topic.syllabus_ref}</p>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                    <Card className="p-6">
                        <SectionHeader title="Difficulty Deep Dive" icon={<BarChart3 className="w-5 h-5 text-slate-500" />} />
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                            <div className="bg-slate-50 p-3 rounded-lg text-center">
                                <p className="text-xs text-slate-400 uppercase">Accuracy Exp.</p>
                                <p className="font-bold text-xl text-slate-700">{t1.difficulty_analysis.expected_accuracy_percent}%</p>
                            </div>
                            <div className="col-span-2 bg-slate-50 p-3 rounded-lg">
                                <p className="text-xs text-slate-400 uppercase mb-2">Complexity Breakdown</p>
                                <div className="flex gap-1 h-2 w-full rounded-full overflow-hidden mb-2">
                                    <div className="bg-blue-400" style={{ flex: t1.difficulty_analysis.complexity_breakdown.conceptual }} title="Conceptual"></div>
                                    <div className="bg-emerald-400" style={{ flex: t1.difficulty_analysis.complexity_breakdown.mathematical }} title="Mathematical"></div>
                                    <div className="bg-amber-400" style={{ flex: t1.difficulty_analysis.complexity_breakdown.problem_solving }} title="Problem Solving"></div>
                                </div>
                                <div className="flex justify-between text-xs text-slate-500">
                                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-blue-400"></div> Conc ({t1.difficulty_analysis.complexity_breakdown.conceptual})</span>
                                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-emerald-400"></div> Math ({t1.difficulty_analysis.complexity_breakdown.mathematical})</span>
                                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-amber-400"></div> Prob ({t1.difficulty_analysis.complexity_breakdown.problem_solving})</span>
                                </div>
                            </div>
                        </div>
                        <div>
                            <h4 className="text-sm font-bold text-slate-800 mb-2">Difficulty Factors</h4>
                            <div className="flex flex-wrap gap-2">
                                {t1.difficulty_analysis.difficulty_factors.map((factor, i) => (
                                    <span key={i} className="px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-sm border border-slate-200">
                                        {factor}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </Card>

                    <Card className="p-6">
                        <SectionHeader title="Step-by-Step Explanation" icon={<Lightbulb className="w-5 h-5 text-amber-500" />} />

                        <div className="mb-6 p-3 bg-amber-50 border border-amber-100 rounded-lg flex flex-col sm:flex-row justify-between items-center text-sm gap-2">
                            <div className="flex items-center gap-2">
                                <Waypoints className="w-4 h-4 text-amber-600" />
                                <span className="font-bold text-amber-800">Approach:</span>
                                <span className="text-amber-900">{t1.step_by_step_solution.approach_type}</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="font-bold text-amber-800">Path:</span>
                                <span className="text-amber-900 font-mono text-xs">{t1.step_by_step_solution.solution_path}</span>
                            </div>
                        </div>

                        <div className="space-y-4">
                            {t1.explanation.step_by_step.map((step, idx) => (
                                <div key={idx} className="flex gap-4">
                                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-xs mt-0.5">
                                        {idx + 1}
                                    </div>
                                    <div className="text-slate-700 leading-relaxed text-sm">
                                        <MathText>{step}</MathText>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-6 pt-6 border-t border-slate-100">
                            <p className="text-sm font-semibold text-slate-900 dark:text-white mb-3">Mathematical Principles:</p>
                            <div className="overflow-x-auto">
                                <table className="min-w-full text-sm text-left">
                                    <thead className="bg-slate-50 text-slate-500 font-medium">
                                        <tr>
                                            <th className="px-3 py-2">Name</th>
                                            <th className="px-3 py-2">Formula</th>
                                            <th className="px-3 py-2">Relevance</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100">
                                        {t1.formulas_principles.map((fp, i) => (
                                            <tr key={i}>
                                                <td className="px-3 py-2 font-medium text-slate-900 dark:text-gray-200">{fp.name}</td>
                                                <td className="px-3 py-2 font-mono text-blue-600 bg-blue-50/50">
                                                    <MathText inline>{(fp.formula || "").toString().startsWith('$') ? fp.formula : '$' + fp.formula + '$'}</MathText>
                                                </td>
                                                <td className="px-3 py-2 text-xs text-slate-500 italic max-w-[150px] truncate" title={fp.relevance}>{fp.relevance}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </Card>

                    <Card className="p-6">
                        <SectionHeader title="Knowledge Graph" icon={<GitBranch className="w-5 h-5 text-purple-500" />} />
                        <div className="space-y-6">
                            <div>
                                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Dependency Tree</h4>
                                <div className="bg-slate-50 p-4 rounded-lg space-y-4 border border-slate-200">
                                    {t1.prerequisites.dependency_tree && Object.entries(t1.prerequisites.dependency_tree).map(([key, reqs]) => (
                                        <div key={key}>
                                            <p className="font-semibold text-slate-800 flex items-center gap-2 text-sm">
                                                <span className="w-2 h-2 rounded-full bg-purple-400"></span>
                                                {key}
                                            </p>
                                            <ul className="ml-2 mt-2 pl-3 border-l-2 border-slate-200 space-y-2">
                                                {reqs.map((r, i) => (
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
                </div>

                <div className="space-y-6">
                    <Card className="p-6">
                        <SectionHeader title="Textbook References" icon={<BookOpen className="w-5 h-5 text-blue-500" />} />
                        <div className="space-y-6">
                            {t1.textbook_references.map((ref, i) => (
                                <div key={i} className="text-sm border-b border-slate-100 last:border-0 pb-4 last:pb-0">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <p className="font-bold text-slate-900 dark:text-white">{ref.book}</p>
                                            <p className="text-slate-600 mb-1 text-xs">by {ref.author}</p>
                                        </div>
                                    </div>

                                    <div className="flex flex-wrap gap-2 mb-2">
                                        <Badge variant={ref.relevance_score > 0.9 ? 'green' : 'yellow'}>{(ref.relevance_score * 100).toFixed(0)}% Match</Badge>
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
                    <Card className="p-6">
                        <SectionHeader title="Video Lectures" icon={<Video className="w-5 h-5 text-red-500" />} />
                        <div className="space-y-4">
                            {t1.video_references.map((ref, i) => (
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

                    <Card className="p-6 bg-gradient-to-br from-slate-800 to-slate-900 text-white border-0">
                        <SectionHeader title="Real World Context" icon={<Factory className="w-5 h-5 text-emerald-400" />} />
                        <div className="space-y-4 mt-2">
                            <div>
                                <p className="text-xs font-bold text-slate-400 uppercase mb-1">Practical Relevance</p>
                                <p className="text-sm text-slate-200 leading-relaxed">
                                    {t1.real_world_applications.practical_relevance}
                                </p>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
};
