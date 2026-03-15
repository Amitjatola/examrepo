import React from 'react';
import {
    BookOpen,
    ArrowRight,
    Wind,
    Plane,
    Zap,
    Box,
    Sigma,
    Activity,
    Layers
} from 'lucide-react';
import SearchBox from './SearchBox';

const SyllabusSelection = ({ syllabusTree, onSubjectSelect, onSearch, query }) => {

    // Icon mapping using Lucide icons for a cleaner look than emojis
    const getSubjectIcon = (subject) => {
        const s = subject.toLowerCase();
        if (s.includes('fluid') || s.includes('aerodynamics')) return <Wind size={20} />;
        if (s.includes('flight')) return <Plane size={20} />;
        if (s.includes('propulsion')) return <Zap size={20} />;
        if (s.includes('structure')) return <Box size={20} />;
        if (s.includes('math')) return <Sigma size={20} />;
        if (s.includes('general')) return <BookOpen size={20} />;
        if (s.includes('vibration') || s.includes('dynamics')) return <Activity size={20} />;
        if (s.includes('material')) return <Layers size={20} />;

        return <BookOpen size={20} />;
    };

    // Color gradients for icons to match YearSelection premium feel
    // We can rotate these or map them to subjects if we want distinct colors
    const getGradientClass = (index) => {
        const gradients = [
            'from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 text-blue-600 dark:text-blue-400 border-blue-500',
            'from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 text-emerald-600 dark:text-emerald-400 border-emerald-500',
            'from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 text-orange-600 dark:text-orange-400 border-orange-500',
            'from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 text-purple-600 dark:text-purple-400 border-purple-500',
            'from-cyan-50 to-sky-50 dark:from-cyan-900/20 dark:to-sky-900/20 text-cyan-600 dark:text-cyan-400 border-cyan-500',
        ];
        return gradients[index % gradients.length];
    };

    return (
        <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark scroll-smooth h-full">
            <div className="max-w-[1200px] mx-auto p-8 space-y-8">

                {/* Header Section */}
                <div className="flex flex-col gap-6">
                    <div className="flex flex-col gap-2">
                        <h1 className="text-3xl font-bold text-slate-900 dark:text-white font-display">Browse by Syllabus</h1>
                        <p className="text-slate-500 dark:text-gray-400 text-lg">Master each subject area with topic-wise practice questions.</p>
                    </div>
                    <div className="max-w-2xl">
                        <SearchBox onSearch={onSearch} initialValue={query} placeholder="Search topics or concepts..." />
                    </div>
                </div>

                {/* Subjects Grid */}
                <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {Object.keys(syllabusTree).map((subject, index) => {
                        const topicCount = syllabusTree[subject]?.length || 0;
                        const icon = getSubjectIcon(subject);
                        const gradientClass = getGradientClass(index);

                        return (
                            <div
                                key={subject}
                                onClick={() => onSubjectSelect(subject)}
                                className={`bg-white dark:bg-card-dark p-5 rounded-xl shadow-sm border border-[#f0f2f4] dark:border-border-dark 
                                         hover:shadow-lg hover:shadow-primary/10 hover:border-primary/30 dark:hover:border-primary/30 
                                         hover:-translate-y-1 cursor-pointer transition-all duration-300 relative overflow-hidden group 
                                         border-t-2 ${gradientClass.split(' ').pop()}`}
                            >

                                <div className="flex flex-col gap-3">
                                    <div className="flex justify-between items-start">
                                        {/* Icon Container with Gradient */}
                                        <div className={`size-10 rounded-lg bg-gradient-to-br ${gradientClass.replace(gradientClass.split(' ').pop(), '')} flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                                            {icon}
                                        </div>
                                    </div>

                                    <div>
                                        {/* Dynamic "Last Attempted" Meta String */}
                                        <span className="text-[10px] font-semibold text-slate-500 dark:text-gray-400 uppercase tracking-wider block mb-1">
                                            {topicCount > 0 ? "Last Attempted: 2 Days Ago" : "Not Started"}
                                        </span>
                                        {/* Subject Name */}
                                        <h3 className="text-base font-bold text-slate-900 dark:text-white mt-1 group-hover:text-primary transition-colors line-clamp-2 leading-tight">
                                            {subject}
                                        </h3>

                                        <div className="mt-4 flex items-center justify-between">
                                            {/* Topic Count Badge darkened to text-slate-600 */}
                                            <div className="flex items-center gap-1.5 bg-slate-50 dark:bg-slate-800/50 px-2 py-1 rounded">
                                                <Layers size={14} className="text-slate-400" />
                                                <span className="text-xs font-semibold tracking-wide text-slate-600 dark:text-gray-300">
                                                    {topicCount} Topics
                                                </span>
                                            </div>
                                            
                                            {/* Small 3-segment difficulty bar */}
                                            <div className="flex gap-0.5 items-end h-3" title="Difficulty Distribution (Easy/Med/Hard)">
                                                <div className="w-1.5 h-[40%] bg-emerald-400 rounded-sm"></div>
                                                <div className="w-1.5 h-[70%] bg-amber-400 rounded-sm"></div>
                                                <div className="w-1.5 h-[100%] bg-rose-400 rounded-sm"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default SyllabusSelection;
