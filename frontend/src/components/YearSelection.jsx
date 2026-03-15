import React, { useState, useEffect } from 'react';
import { Calendar, ArrowRight, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const YearSelection = ({ onYearSelect }) => {
    const { user, openLogin } = useAuth();
    const [yearCounts, setYearCounts] = useState({});
    const [loading, setLoading] = useState(true);

    // Generate years from 2025 down to 2007 (all years with available questions)
    const years = Array.from({ length: 2025 - 2007 + 1 }, (_, i) => 2025 - i);

    useEffect(() => {
        const fetchYearCounts = async () => {
            try {
                const response = await fetch(`${API_BASE}/search/year-counts`);
                if (response.ok) {
                    const data = await response.json();
                    setYearCounts(data);
                }
            } catch (error) {
                console.error('Error fetching year counts:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchYearCounts();
    }, []);

    return (
        <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark scroll-smooth h-full">
            <div className="max-w-[1200px] mx-auto p-8 space-y-8">

                {/* Header Section */}
                <div className="flex flex-col gap-2">
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white font-display">Practice by Year</h1>
                    <p className="text-slate-500 dark:text-gray-400 text-lg">Select a year to attempt previous year question papers.</p>
                </div>

                {/* Years Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                    {years.map((year) => {
                        const count = yearCounts[year] || 0;
                        // Mock progress for demo purposes (e.g. 2024 is in progress, 2023 is completed, rest not started)
                        const progress = user ? (year === 2024 ? Math.floor(count * 0.15) : (year === 2023 ? count : 0)) : 0;
                        
                        return (
                            <div
                                key={year}
                                onClick={() => onYearSelect(year)}
                                className="bg-white dark:bg-card-dark p-6 rounded-2xl shadow-sm border border-[#f0f2f4] dark:border-border-dark 
                                         hover:shadow-xl hover:shadow-primary/10 hover:border-primary/30 dark:hover:border-primary/30 
                                         hover:-translate-y-1 cursor-pointer transition-all duration-300 group relative overflow-hidden"
                            >
                                <div className="absolute top-0 right-0 p-3 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <div className="bg-primary/10 text-primary p-1.5 rounded-full">
                                        <ArrowRight size={16} />
                                    </div>
                                </div>

                                    <div className="flex flex-col gap-4">
                                        <div className="flex justify-between items-start">
                                            <div className="size-12 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 text-primary flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                                                <Calendar size={24} />
                                            </div>
                                            {!loading && user && progress > 0 && (
                                                <div className="flex flex-col items-end gap-1">
                                                    {/* Status Badge */}
                                                    {progress < count ? (
                                                        <span className="text-[10px] font-bold text-amber-600 bg-amber-50 dark:bg-amber-500/10 dark:text-amber-400 px-2 py-0.5 rounded uppercase tracking-wider">In Progress</span>
                                                    ) : (
                                                        <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-500/10 dark:text-emerald-400 px-2 py-0.5 rounded uppercase tracking-wider">Completed</span>
                                                    )}
                                                    <div className="text-right mt-1">
                                                        <div className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-tight">Progress</div>
                                                        <div className="text-xs font-black text-slate-900 dark:text-white">
                                                            {progress}/{count}
                                                        </div>
                                                    </div>
                                                </div>
                                            )}
                                        </div>

                                        <div>
                                            <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">GATE AEROSPACE</span>
                                            <h3 className="text-2xl font-bold text-slate-900 dark:text-white mt-1 group-hover:text-primary transition-colors">{year}</h3>
                                        </div>

                                        <div className="space-y-2">
                                            <div className="flex items-center gap-2">
                                                <span className="text-xs font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-2 py-1 rounded-md">
                                                    Full Paper
                                                </span>
                                                <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                                                    {loading ? (
                                                        <Loader2 size={12} className="animate-spin inline" />
                                                    ) : (
                                                        `${count} Questions`
                                                    )}
                                                </span>
                                            </div>
                                            
                                            {!loading && user && progress > 0 && (
                                                <div className="w-full h-1.5 bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                                                    <div 
                                                        className="h-full bg-primary rounded-full transition-all duration-500"
                                                        style={{ width: `${(progress / count) * 100}%` }}
                                                    ></div>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Hover State Resume Button */}
                                    {user && progress > 0 && progress < count && (
                                        <div className="absolute inset-0 bg-white/90 dark:bg-[#15192b]/90 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col items-center justify-center pointer-events-none group-hover:pointer-events-auto">
                                            <div className="flex flex-col items-center gap-3 transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
                                                <div className="size-12 rounded-full bg-primary/10 text-primary flex items-center justify-center mx-auto mb-1">
                                                    <ArrowRight size={24} />
                                                </div>
                                                <span className="text-slate-900 dark:text-white font-semibold flex items-center justify-center gap-2">
                                                    Resume Paper
                                                </span>
                                                <div className="bg-slate-100 dark:bg-white/5 rounded-full h-1 w-16 overflow-hidden">
                                                    <div className="h-full bg-primary rounded-full" style={{ width: `${(progress / count) * 100}%` }}></div>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default YearSelection;
