import React, { useState, useEffect } from 'react'
import { Calendar, ArrowRight, Loader2 } from 'lucide-react'
import { api } from '../utils/api'

/**
 * Normalize API JSON: year keys may arrive as strings ("2025") after JSON.parse.
 */
const normalizeYearCounts = (raw) => {
    if (!raw || typeof raw !== 'object') return {}
    const out = {}
    for (const [key, value] of Object.entries(raw)) {
        const y = parseInt(String(key), 10)
        if (!Number.isFinite(y)) continue
        const n = typeof value === 'number' ? value : parseInt(String(value), 10)
        out[y] = Number.isFinite(n) ? n : 0
    }
    return out
}

const YearSelection = ({ onYearSelect }) => {
    const [yearCounts, setYearCounts] = useState({})
    const [loading, setLoading] = useState(true)
    const [loadError, setLoadError] = useState(null)

    const years = Array.from({ length: 2025 - 2007 + 1 }, (_, i) => 2025 - i)

    useEffect(() => {
        const fetchYearCounts = async () => {
            setLoadError(null)
            try {
                const data = await api.get('/search/year-counts')
                setYearCounts(normalizeYearCounts(data))
            } catch (error) {
                console.error('Error fetching year counts:', error)
                setYearCounts({})
                setLoadError(
                    error?.message ||
                        'Could not load question counts. Check API URL (VITE_API_URL) and backend logs.',
                )
            } finally {
                setLoading(false)
            }
        }
        fetchYearCounts()
    }, [])

    return (
        <div className="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark scroll-smooth h-full">
            <div className="max-w-[1200px] mx-auto p-8 space-y-8">
                <div className="flex flex-col gap-2">
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white font-display">
                        Practice by Year
                    </h1>
                    <p className="text-slate-500 dark:text-gray-400 text-lg">
                        Select a year to attempt previous year question papers.
                    </p>
                </div>

                {loadError && (
                    <div
                        className="rounded-xl border border-amber-200 dark:border-amber-900/50 bg-amber-50 dark:bg-amber-900/20 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
                        role="alert"
                    >
                        <p className="font-semibold mb-1">Question counts unavailable</p>
                        <p>{loadError}</p>
                        <p className="mt-2 text-xs opacity-90">
                            Production builds must set{' '}
                            <code className="rounded bg-white/50 dark:bg-black/30 px-1">
                                VITE_API_URL
                            </code>{' '}
                            to your API Gateway base including{' '}
                            <code className="rounded bg-white/50 dark:bg-black/30 px-1">/api/v1</code>{' '}
                            (example:{' '}
                            <code className="rounded bg-white/50 dark:bg-black/30 px-1 break-all">
                                https://xxxx.execute-api.ap-south-1.amazonaws.com/api/v1
                            </code>
                            ). Redeploy the frontend after changing env vars.
                        </p>
                    </div>
                )}

                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                    {years.map((year) => {
                        const count = yearCounts[year] ?? 0

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
                                    <div className="flex items-start">
                                        <div className="size-12 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 text-primary flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                                            <Calendar size={24} />
                                        </div>
                                    </div>

                                    <div>
                                        <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                            GATE AEROSPACE
                                        </span>
                                        <h3 className="text-2xl font-bold text-slate-900 dark:text-white mt-1 group-hover:text-primary transition-colors">
                                            {year}
                                        </h3>
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
                                    </div>
                                </div>
                            </div>
                        )
                    })}
                </div>
            </div>
        </div>
    )
}

export default YearSelection
