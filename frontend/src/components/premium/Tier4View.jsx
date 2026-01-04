import React from 'react';
import { Card, SectionHeader, Badge } from './ui';
import { Server, Code, DollarSign, Activity, Cpu, Database, CheckSquare, Clock, AlertTriangle, FileText } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export const Tier4View = ({ data }) => {
    if (!data) return null;
    const { tier_4_metadata_and_future: t4, tier_0_classification: t0 } = data;
    const models = t4.model_meta.models_used;

    const tokenData = Object.entries(t4.token_usage.per_model).map(([name, usage]) => ({
        name: name.replace(/_/g, ' '),
        input: usage.input,
        output: usage.output
    }));

    return (
        <div className="space-y-8 pb-20">

            {/* Overview Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card className="p-4 bg-white border-l-4 border-l-blue-500">
                    <p className="text-xs text-slate-500 uppercase font-bold">Pipeline Version</p>
                    <p className="font-mono text-lg font-bold text-slate-900 dark:text-white">{t4.model_meta.pipeline_version}</p>
                </Card>
                <Card className="p-4 bg-white border-l-4 border-l-emerald-500">
                    <p className="text-xs text-slate-500 uppercase font-bold">Quality Band</p>
                    <p className="font-mono text-lg font-bold text-emerald-700">{t4.quality_score.band} ({t4.quality_score.overall})</p>
                </Card>
                <Card className="p-4 bg-white border-l-4 border-l-purple-500">
                    <p className="text-xs text-slate-500 uppercase font-bold">Total Cost</p>
                    <p className="font-mono text-lg font-bold text-purple-700">{t4.cost_breakdown.currency === 'USD' ? '$' : t4.cost_breakdown.currency}{t4.cost_breakdown.total_cost.toFixed(5)}</p>
                </Card>
                <Card className="p-4 bg-white border-l-4 border-l-orange-500">
                    <p className="text-xs text-slate-500 uppercase font-bold">Processing Time</p>
                    <p className="font-mono text-lg font-bold text-orange-700">{t4.processing_time.total_seconds.toFixed(2)}s</p>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Column 1: Classification & Complexity DNA */}
                <div className="space-y-6">
                    <Card className="p-6">
                        <SectionHeader title="Complexity DNA (Tier 0)" icon={<Activity className="w-5 h-5 text-slate-500" />} />
                        <div className="space-y-4">
                            <div className="flex flex-wrap gap-2 mb-4">
                                <Badge variant="blue">{t0.content_type}</Badge>
                                <Badge variant="gray">{t0.media_type}</Badge>
                                <Badge variant="yellow">{t0.weight_strategy}</Badge>
                                <Badge variant="red">Diff Score: {t0.difficulty_score}</Badge>
                            </div>

                            <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 text-xs space-y-1">
                                <div className="flex justify-between">
                                    <span className="text-slate-500">Model:</span>
                                    <span className="font-mono">{t0.classifier_model}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-slate-500">Method:</span>
                                    <span className="font-mono">{t0.classification_method}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-slate-500">Confidence:</span>
                                    <span className="font-mono font-bold text-emerald-600">{(t0.classification_confidence * 100).toFixed(1)}%</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-slate-500">GPT-5.1:</span>
                                    <span className="font-mono">{t0.use_gpt51 ? 'Enabled' : 'Disabled'}</span>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <p className="text-xs font-bold text-slate-400 uppercase">Flags Detected</p>
                                {t0.complexity_flags && Object.entries(t0.complexity_flags).map(([key, value]) => (
                                    <div key={key} className={`flex items-center justify-between p-2 rounded ${value ? 'bg-slate-100' : 'opacity-50'}`}>
                                        <span className="text-sm font-mono text-slate-700">{key.replace(/_/g, ' ')}</span>
                                        {value ? <CheckSquare className="w-4 h-4 text-emerald-500" /> : <span className="text-xs text-slate-300">False</span>}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </Card>

                    <Card className="p-6">
                        <SectionHeader title="Processing Timeline" icon={<Clock className="w-5 h-5 text-orange-500" />} />
                        <div className="space-y-3">
                            <div className="flex justify-between text-sm">
                                <span className="text-slate-600">Bottleneck</span>
                                <span className="font-mono text-orange-600 font-bold">{t4.processing_time.bottleneck_stage}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-slate-600">Parallel Gen</span>
                                <span className="font-mono">{t4.processing_time.parallel_generation_time.toFixed(3)}s</span>
                            </div>
                            <div className="flex justify-between text-sm border-b pb-2 mb-2">
                                <span className="text-slate-600">Debate Time</span>
                                <span className="font-mono">{t4.processing_time.debate_time.toFixed(3)}s</span>
                            </div>
                            <div className="space-y-1">
                                {Object.entries(t4.processing_time.per_stage).map(([stage, time]) => {
                                    const pct = (time / t4.processing_time.total_seconds) * 100;
                                    return (
                                        <div key={stage} className="space-y-0.5">
                                            <div className="flex justify-between text-xs text-slate-500">
                                                <span>{stage}</span>
                                                <span>{time.toFixed(3)}s</span>
                                            </div>
                                            <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                                                <div className="h-full bg-orange-400 rounded-full" style={{ width: `${pct}%` }}></div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Column 2: AI Models & Consensus */}
                <div className="lg:col-span-2 space-y-6">
                    <Card className="p-6">
                        <SectionHeader title="AI Council (Model Consensus)" icon={<Cpu className="w-5 h-5 text-blue-500" />} />

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                            <div>
                                <div className="flex justify-between items-baseline mb-3">
                                    <h4 className="text-sm font-bold text-slate-900 dark:text-white">Model Weights & Votes</h4>
                                    <span className="text-[10px] text-slate-400">
                                        {t4.model_meta.model_count} Models | {t4.model_meta.weight_strategy}
                                    </span>
                                </div>
                                <div className="space-y-3">
                                    {t4.model_meta.models_used.map((model) => (
                                        <div key={model} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-100">
                                            <div className="flex flex-col">
                                                <span className="font-bold text-sm text-slate-800">{model}</span>
                                                <span className="text-xs text-slate-500">Weight: {t4.model_meta.weights_applied[model]}</span>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-xs text-slate-400">Tokens</p>
                                                <p className="font-mono text-xs text-slate-700">{t4.token_usage.per_model[model]?.total.toLocaleString()}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <h4 className="text-sm font-bold text-slate-900 dark:text-white mb-3">Quality & Meta</h4>
                                <div className="grid grid-cols-2 gap-3 mb-4">
                                    {Object.entries(t4.quality_score.metrics).map(([key, val]) => (
                                        <div key={key} className="bg-white p-3 rounded border border-slate-200">
                                            <p className="text-xs text-slate-400 uppercase mb-1">{key.replace(/_/g, ' ')}</p>
                                            <p className="font-mono font-bold text-slate-700">{(val * 100).toFixed(1)}%</p>
                                        </div>
                                    ))}
                                </div>
                                <div className="p-3 bg-blue-50 rounded-lg text-xs text-blue-800 grid grid-cols-2 gap-2">
                                    <p><strong>Method:</strong> {t4.model_meta.consensus_method}</p>
                                    <p><strong>Converged:</strong> {t4.model_meta.converged_fields_count} fields</p>
                                    <p><strong>Debated:</strong> {t4.model_meta.debated_fields_count} fields</p>
                                    <p><strong>Rounds:</strong> {t4.model_meta.debate_rounds}</p>
                                    <p><strong>GPT-5.1 Debate:</strong> {t4.model_meta.gpt51_added_in_debate ? 'Yes' : 'No'}</p>
                                    <p><strong>Review Flags:</strong> {t4.model_meta.flagged_for_review.length}</p>
                                </div>
                            </div>
                        </div>
                    </Card>

                    <Card className="p-6">
                        <SectionHeader title="Token Usage Analysis" icon={<BarChart className="w-5 h-5 text-blue-500" />} />
                        <div className="h-64 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={tokenData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                    <XAxis type="number" fontSize={12} />
                                    <YAxis dataKey="name" type="category" width={120} fontSize={11} />
                                    <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '8px' }} />
                                    <Bar dataKey="input" stackId="a" fill="#0ea5e9" name="Input" radius={[0, 4, 4, 0]} barSize={20} />
                                    <Bar dataKey="output" stackId="a" fill="#3b82f6" name="Output" radius={[0, 4, 4, 0]} barSize={20} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
};
