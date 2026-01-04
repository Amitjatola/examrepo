import React from 'react';
import { Card, SectionHeader, MathText } from './ui';
import { Network, Search, ArrowRightLeft, Layers, Sparkles } from 'lucide-react';

export const Tier3View = ({ data }) => {
    if (!data) return null;
    const t3 = data;

    return (
        <div className="space-y-6">

            {/* Top Row: Connections & Search */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="p-6">
                    <SectionHeader title="Cross-Disciplinary Connections" icon={<Network className="w-5 h-5 text-purple-500" />} />
                    <div className="space-y-3">
                        {t3.connections_to_other_subjects && Object.entries(t3.connections_to_other_subjects).map(([subject, desc], i) => (
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
                            {t3.search_keywords.map((kw, i) => (
                                <span key={i} className="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-full text-xs transition-colors cursor-default border border-slate-200">
                                    #{kw}
                                </span>
                            ))}
                        </div>
                    </Card>
                    <Card className="p-6">
                        <SectionHeader title="Deeper Dive Topics" icon={<Layers className="w-5 h-5 text-indigo-500" />} />
                        <ul className="list-disc pl-5 space-y-1">
                            {t3.deeper_dive_topics.map((topic, i) => (
                                <li key={i} className="text-sm text-indigo-900 font-medium">{topic}</li>
                            ))}
                        </ul>
                    </Card>
                </div>
            </div>

            {/* Bottom: Alternative Methods */}
            <Card className="p-6 bg-slate-50 border-slate-200">
                <SectionHeader title="Alternative Methods" icon={<ArrowRightLeft className="w-5 h-5 text-emerald-600" />} />
                <div className="grid grid-cols-1 gap-4">
                    {t3.alternative_methods.map((method, i) => (
                        <div key={i} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                            <h4 className="font-bold text-slate-900 dark:text-white mb-2 text-lg">{method.name}</h4>
                            <p className="text-slate-700 mb-4 text-sm"><MathText>{method.description}</MathText></p>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                <div className="bg-slate-50 p-3 rounded border border-slate-100">
                                    <span className="text-xs font-bold text-slate-400 uppercase block mb-1">Pros & Cons</span>
                                    <MathText>{method.pros_cons}</MathText>
                                </div>
                                <div className="bg-emerald-50 p-3 rounded border border-emerald-100 text-emerald-900">
                                    <span className="text-xs font-bold text-emerald-700 uppercase block mb-1">When to use</span>
                                    {method.when_to_use}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </Card>
        </div>
    );
};
