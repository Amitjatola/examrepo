import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Clock } from 'lucide-react';
import { MathText } from './ui';

export const FlipCard = ({ card }) => {
    const [isFlipped, setIsFlipped] = useState(false);
    const [isAnimating, setIsAnimating] = useState(false);

    const handleFlip = () => {
        if (!isAnimating) {
            setIsFlipped(!isFlipped);
            setIsAnimating(true);
        }
    };

    return (
        <div
            className="h-72 sm:h-80 w-full min-w-0 min-h-0 cursor-pointer perspective-1000"
            onClick={handleFlip}
        >
            <motion.div
                className="relative w-full h-full min-h-0 max-h-full"
                initial={false}
                animate={{ rotateY: isFlipped ? 180 : 0 }}
                transition={{ duration: 0.6, animationDirection: "normal" }}
                onAnimationComplete={() => setIsAnimating(false)}
                style={{ transformStyle: "preserve-3d" }}
            >
                {/* Front */}
                <div
                    className="absolute inset-0 bg-white dark:bg-slate-900 p-4 sm:p-5 rounded-xl shadow-sm border border-slate-200 dark:border-white/10 flex flex-col overflow-hidden backface-hidden min-h-0"
                    style={{ backfaceVisibility: 'hidden' }}
                >
                    <div className="flex min-h-0 flex-1 flex-col gap-2">
                        <span className="shrink-0 text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                            {card.card_type}
                        </span>
                        <div className="min-h-0 min-w-0 flex-1 overflow-y-auto overflow-x-hidden overscroll-contain [scrollbar-gutter:stable]">
                            <div className="min-w-0 max-w-full whitespace-normal break-words text-base font-semibold leading-snug text-slate-800 [overflow-wrap:anywhere] sm:text-lg dark:text-slate-100 [&_.katex]:max-w-full [&_.katex]:text-inherit [&_.katex-display]:max-w-full [&_.katex-display]:overflow-x-auto">
                                <MathText>{card.front}</MathText>
                            </div>
                        </div>
                    </div>
                    <div className="text-xs text-slate-400 dark:text-slate-500 flex justify-between items-center gap-2 border-t border-slate-50 dark:border-white/10 pt-3 mt-3 shrink-0">
                        <span className="capitalize badge-gray px-2 py-0.5 rounded bg-slate-100 dark:bg-white/10 text-slate-500 dark:text-slate-400 truncate max-w-[50%]">
                            {card.difficulty}
                        </span>
                        <span className="flex items-center gap-1 font-mono shrink-0">
                            <Clock className="w-3 h-3 shrink-0" /> {card.time_limit_seconds}s
                        </span>
                    </div>
                </div>

                {/* Back */}
                <div
                    className="absolute inset-0 flex min-h-0 flex-col overflow-hidden rounded-xl bg-slate-800 p-4 sm:p-5 shadow-md backface-hidden"
                    style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
                >
                    <div className="min-h-0 min-w-0 flex-1 overflow-y-auto overflow-x-hidden overscroll-contain [scrollbar-gutter:stable]">
                        <div className="min-w-0 max-w-full whitespace-normal break-words text-left text-sm font-medium leading-relaxed text-white [overflow-wrap:anywhere] sm:text-base [&_.katex]:max-w-full [&_.katex]:text-inherit [&_.katex-display]:max-w-full [&_.katex-display]:overflow-x-auto">
                            <MathText inline>{card.back}</MathText>
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};
