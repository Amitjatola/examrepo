import React from 'react';
import { Card, Badge, MathText } from './ui';
import { CheckSquare, Activity } from 'lucide-react';

export const Tier0View = ({ data }) => {
    if (!data) return null;

    return (
        <div className="space-y-6">
            <Card className="border-l-4 border-l-blue-500 p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Classification</h3>
                        <p className="text-slate-600 mb-4 text-sm leading-relaxed">
                            <MathText>{data.classification_reasoning}</MathText>
                        </p>
                        <div className="flex flex-wrap gap-2 mb-4">
                            <Badge variant="blue">{data.content_type?.replace('_', ' ')}</Badge>
                            <Badge variant="green">Difficulty: {data.difficulty_score}/5</Badge>
                            <Badge variant="gray">{data.media_type}</Badge>
                        </div>

                        <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-xs text-slate-500 bg-slate-50 p-3 rounded border border-slate-100">
                            <div><span className="font-semibold text-slate-700">Method:</span> {data.classification_method}</div>
                            <div><span className="font-semibold text-slate-700">Model:</span> {data.classifier_model}</div>
                            <div><span className="font-semibold text-slate-700">Confidence:</span> {(data.classification_confidence * 100).toFixed(0)}%</div>
                            <div><span className="font-semibold text-slate-700">GPT-5.1:</span> {data.use_gpt51 ? 'Yes' : 'No'}</div>
                            <div className="col-span-2"><span className="font-semibold text-slate-700">Strategy:</span> {data.weight_strategy}</div>
                            <div className="col-span-2"><span className="font-semibold text-slate-700">Type:</span> {data.combined_type}</div>
                        </div>
                    </div>
                    <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                        <div className="flex items-center gap-2 mb-3">
                            <Activity className="w-4 h-4 text-slate-400" />
                            <h4 className="text-xs font-bold uppercase text-slate-400">Complexity Flags</h4>
                        </div>
                        <div className="grid grid-cols-1 gap-2">
                            {data.complexity_flags && Object.entries(data.complexity_flags).map(([key, value]) => (
                                <div key={key} className={`text-xs flex items-center gap-2 ${value ? 'text-rose-600 font-bold' : 'text-slate-400'}`}>
                                    <div className={`w-2 h-2 rounded-full flex-shrink-0 ${value ? 'bg-rose-500' : 'bg-slate-300'}`} />
                                    {key.replace(/_/g, ' ')}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </Card>
        </div>
    );
};
