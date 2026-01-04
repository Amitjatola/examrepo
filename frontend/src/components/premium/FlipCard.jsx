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
        <div className="h-48 w-full cursor-pointer perspective-1000" onClick={handleFlip}>
            <motion.div
                className="relative w-full h-full"
                initial={false}
                animate={{ rotateY: isFlipped ? 180 : 0 }}
                transition={{ duration: 0.6, animationDirection: "normal" }}
                onAnimationComplete={() => setIsAnimating(false)}
                style={{ transformStyle: "preserve-3d" }}
            >
                {/* Front */}
                <div className="absolute w-full h-full bg-white p-5 rounded-xl shadow-sm border border-slate-200 flex flex-col justify-between backface-hidden" style={{ backfaceVisibility: 'hidden' }}>
                    <div>
                        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">{card.card_type}</span>
                        <div className="font-semibold text-slate-800 mt-3 text-lg leading-snug">
                            <MathText>{card.front}</MathText>
                        </div>
                    </div>
                    <div className="text-xs text-slate-400 flex justify-between items-center border-t border-slate-50 pt-3">
                        <span className="capitalize badge-gray px-2 py-0.5 rounded bg-slate-100 text-slate-500">{card.difficulty}</span>
                        <span className="flex items-center gap-1 font-mono"><Clock className="w-3 h-3" /> {card.time_limit_seconds}s</span>
                    </div>
                </div>

                {/* Back */}
                <div
                    className="absolute w-full h-full bg-slate-800 p-6 rounded-xl shadow-md flex flex-col justify-center text-center backface-hidden"
                    style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
                >
                    <div className="text-white text-base font-medium leading-relaxed">
                        <MathText inline>{card.back}</MathText>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};
