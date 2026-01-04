import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import LatexRenderer from '../LatexRenderer';

export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

export const Card = ({ children, className, title, icon }) => {
    return (
        <div className={cn("bg-white dark:bg-card-dark rounded-xl shadow-sm border border-slate-200 dark:border-border-dark overflow-hidden", className)}>
            {(title || icon) && (
                <div className="px-6 py-4 border-b border-slate-100 dark:border-border-dark flex items-center gap-3 bg-slate-50/50 dark:bg-background-dark/50">
                    {icon && <div className="text-slate-500 dark:text-gray-400">{icon}</div>}
                    {title && <h3 className="font-semibold text-slate-900 dark:text-white">{title}</h3>}
                </div>
            )}
            <div className={cn(!title && !icon ? "" : "")}>
                {children}
            </div>
        </div>
    );
};

export const Badge = ({ children, variant = "gray", className }) => {
    const variants = {
        gray: "bg-slate-100 text-slate-600 border-slate-200",
        blue: "bg-blue-50 text-blue-700 border-blue-100",
        green: "bg-emerald-50 text-emerald-700 border-emerald-100",
        red: "bg-rose-50 text-rose-700 border-rose-100",
        yellow: "bg-amber-50 text-amber-700 border-amber-100",
        purple: "bg-violet-50 text-violet-700 border-violet-100",
    };

    return (
        <span className={cn("px-2.5 py-0.5 rounded-full text-xs font-medium border", variants[variant] || variants.gray, className)}>
            {children}
        </span>
    );
};

export const SectionHeader = ({ title, icon, subtitle }) => {
    return (
        <div className="flex items-start gap-4 mb-6">
            <div className="p-2 bg-slate-100 dark:bg-slate-800 rounded-lg text-slate-600 dark:text-gray-400">
                {icon}
            </div>
            <div>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white leading-tight">{title}</h2>
                {subtitle && <p className="text-sm text-slate-500 dark:text-gray-400 mt-1">{subtitle}</p>}
            </div>
        </div>
    );
};

export const MathText = ({ children, inline = false }) => {
    if (!children) return null;
    return <LatexRenderer text={children} inline={inline} />;
};
