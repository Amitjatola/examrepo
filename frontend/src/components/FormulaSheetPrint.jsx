import React from 'react'
import LatexRenderer from './LatexRenderer'
import { extractFormulaBlocksFromTier1 } from '../utils/formulaBlocks'

/**
 * Printable formula sheet for one question — opens browser print dialog via window.print().
 */
const FormulaSheetPrint = ({ open, onClose, question }) => {
    if (!open || !question) return null

    const tier1 = question.tier_1_core_research || {}
    const blocks = extractFormulaBlocksFromTier1(tier1)

    const handlePrint = () => {
        window.print()
    }

    return (
        <div
            className="fixed inset-0 z-[200] flex items-center justify-center p-4"
            role="dialog"
            aria-modal="true"
            aria-label="Formula sheet print preview"
        >
            <button
                type="button"
                className="absolute inset-0 bg-black/60 backdrop-blur-sm no-print cursor-default"
                aria-label="Close formula sheet overlay"
                onClick={onClose}
            />
            <div className="relative bg-white dark:bg-card-dark max-w-3xl w-full max-h-[90vh] overflow-hidden rounded-2xl border border-slate-200 dark:border-border-dark shadow-2xl flex flex-col print:max-h-none print:shadow-none print:border-0 print:w-full">
                <div className="flex justify-between items-center px-6 py-4 border-b border-slate-200 dark:border-border-dark shrink-0 no-print">
                    <div>
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white">Formula sheet</h2>
                        <p className="text-xs text-slate-500 dark:text-slate-400">{question.question_id}</p>
                    </div>
                    <div className="flex gap-2">
                        <button
                            type="button"
                            onClick={handlePrint}
                            className="px-4 py-2 rounded-lg bg-primary text-white text-sm font-semibold hover:bg-primary/90 cursor-pointer"
                        >
                            Print / PDF
                        </button>
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 rounded-lg border border-slate-200 dark:border-border-dark text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-white/5 cursor-pointer"
                        >
                            Close
                        </button>
                    </div>
                </div>
                <div className="overflow-y-auto p-6 formula-print-root print:overflow-visible">
                    {blocks.length === 0 ? (
                        <p className="text-slate-500 dark:text-slate-400 text-sm italic">No formulas recorded for this question.</p>
                    ) : (
                        <div className="space-y-6">
                            {blocks.map((f) => (
                                <section key={f.key} className="border border-slate-100 dark:border-white/10 rounded-xl p-4">
                                    <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-2">{f.title}</h3>
                                    <div className="text-slate-800 dark:text-slate-200 text-base leading-relaxed">
                                        <LatexRenderer text={f.body} />
                                    </div>
                                </section>
                            ))}
                        </div>
                    )}
                </div>
            </div>
            <style>{`
                @media print {
                  .no-print { display: none !important; }
                  body { background: white !important; }
                }
              `}</style>
        </div>
    )
}

export default FormulaSheetPrint
