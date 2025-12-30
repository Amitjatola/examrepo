import React, { useState, useEffect } from 'react';
import { Calendar, ArrowRight, Loader2 } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const YearSelection = ({ onYearSelect }) => {
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
                                    <div className="size-12 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 text-primary flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                                        <Calendar size={24} />
                                    </div>

                                    <div>
                                        <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">GATE AEROSPACE</span>
                                        <h3 className="text-2xl font-bold text-slate-900 dark:text-white mt-1 group-hover:text-primary transition-colors">{year}</h3>
                                    </div>

                                    <div className="mt-2 flex items-center gap-2">
                                        <span className="text-xs font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-2 py-1 rounded-md">
                                            Full Paper
                                        </span>
                                        <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                                            {loading ? (
                                                <Loader2 size={12} className="animate-spin inline" />
                                            ) : (
                                                `${count} Question${count !== 1 ? 's' : ''}`
                                            )}
                                        </span>
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

export default YearSelection;
