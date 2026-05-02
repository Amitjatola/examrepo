import React from 'react';
import { CalendarDays, LayoutDashboard } from 'lucide-react';

const SmartPlannerStub = ({ onOpenDashboard }) => {
    return (
        <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark h-full">
            <div className="max-w-2xl mx-auto p-8 md:p-12 flex flex-col gap-6">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold w-fit">
                    <CalendarDays size={14} />
                    Smart Planner
                </div>
                <h1 className="text-3xl md:text-4xl font-black text-slate-900 dark:text-white font-display tracking-tight">
                    Scheduling upgrades are coming
                </h1>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                    Full adaptive schedules stay on the roadmap. Today your{' '}
                    <span className="font-semibold text-slate-900 dark:text-white">Study planner</span> controls (target band,
                    time left, Smart/Yield modes) live on the Dashboard — same knobs, honest analytics underneath.
                </p>
                <button
                    type="button"
                    onClick={onOpenDashboard}
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary hover:bg-primary/90 text-white px-5 py-3 text-sm font-bold shadow-lg shadow-primary/25 cursor-pointer"
                >
                    <LayoutDashboard size={18} />
                    Open Dashboard planner
                </button>
            </div>
        </div>
    );
};

export default SmartPlannerStub;
