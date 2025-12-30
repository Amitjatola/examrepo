import React, { useState, useRef, useEffect } from 'react';
import { Search, Bell, Sun, Moon, ChevronRight, Menu, User, LogOut, LogIn } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Header = ({ toggleTheme, theme, showSearch = true, variant = 'default', onBack, onToggleSidebar, breadcrumbs = [] }) => {
    const isDark = theme === 'dark';
    const isDetail = variant === 'detail';
    const { user, openLogin, logout } = useAuth();
    const [showUserMenu, setShowUserMenu] = useState(false);
    const menuRef = useRef(null);

    // Close menu when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (menuRef.current && !menuRef.current.contains(event.target)) {
                setShowUserMenu(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    return (
        <header className={`border-b border-[#f0f2f4] dark:border-border-dark bg-white dark:bg-card-dark flex items-center px-6 justify-between shrink-0 z-10 transition-colors duration-300 ${isDetail ? 'py-3 shadow-sm' : 'h-20 px-8'}`}>

            {/* Mobile/Sidebar Toggle Button */}
            <button
                onClick={onToggleSidebar}
                className="mr-4 p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors cursor-pointer"
            >
                <Menu size={24} />
            </button>

            {/* Left Section: Search (Default) OR Breadcrumbs (Detail) */}
            <div className={`flex-1 ${isDetail ? '' : 'max-w-xl mr-8'}`}>
                {isDetail ? (
                    /* Breadcrumbs */
                    <div className="hidden md:flex flex-wrap gap-2 items-center">
                        {breadcrumbs.length > 0 ? (
                            breadcrumbs.map((crumb, index) => (
                                <React.Fragment key={index}>
                                    <button
                                        onClick={crumb.onClick}
                                        className={`text-sm font-medium transition-colors cursor-pointer ${index === breadcrumbs.length - 1 ? 'text-slate-900 dark:text-white font-semibold cursor-default' : 'text-[#617589] dark:text-gray-400 hover:text-primary'}`}
                                    >
                                        {crumb.label}
                                    </button>
                                    {index < breadcrumbs.length - 1 && <ChevronRight size={16} className="text-[#617589]" />}
                                </React.Fragment>
                            ))
                        ) : (
                            // Fallback if no breadcrumbs provided but in detail view
                            <div className="flex items-center gap-2">
                                <button onClick={onBack} className="text-[#617589] dark:text-gray-400 text-sm font-medium hover:text-primary transition-colors cursor-pointer">Back</button>
                            </div>
                        )}
                    </div>
                ) : (
                    /* Main Search Bar */
                    <div className={`relative group ${!showSearch ? 'invisible' : ''}`}>
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Search className="text-[#617589] dark:text-gray-500" size={20} />
                        </div>
                        <input
                            type="text"
                            className="block w-full pl-10 pr-3 py-2.5 border-none rounded-xl leading-5 bg-[#f0f2f4] dark:bg-background-dark/50 text-slate-900 dark:text-white placeholder-[#617589] focus:outline-none focus:ring-2 focus:ring-primary/50 sm:text-sm transition-all shadow-none"
                            placeholder="Search for questions, topics, or exams..."
                        />
                    </div>
                )}
            </div>

            {/* Right Section */}
            <div className={`flex items-center ${isDetail ? 'gap-6 flex-1 justify-end' : 'gap-6'}`}>
                {/* Detail View Small Search */}
                {isDetail && (
                    <label className="hidden sm:flex flex-col min-w-40 w-full max-w-xs h-10">
                        <div className="flex w-full flex-1 items-stretch rounded-lg h-full relative">
                            <div className="text-[#617589] absolute left-3 top-1/2 -translate-y-1/2 flex items-center justify-center pointer-events-none">
                                <Search size={20} />
                            </div>
                            <input
                                className="flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 border border-transparent bg-[#f0f2f4] dark:bg-background-dark/50 h-full placeholder:text-[#617589] pl-10 pr-4 text-sm font-normal leading-normal transition-all"
                                placeholder="Search questions..."
                            />
                        </div>
                    </label>
                )}

                {/* Actions */}
                <div className="flex items-center gap-2 md:gap-6">
                    {!isDetail && (
                        <button className="relative p-2 text-[#617589] dark:text-gray-400 hover:bg-[#f0f2f4] dark:hover:bg-white/5 rounded-full transition-colors cursor-pointer">
                            <Bell size={24} />
                            <span className="absolute top-2 right-2 size-2 bg-red-500 rounded-full border-2 border-white dark:border-card-dark"></span>
                        </button>
                    )}

                    {isDetail && (
                        <button className="relative flex items-center justify-center rounded-lg size-10 bg-[#f0f2f4] dark:bg-background-dark/50 text-slate-900 dark:text-white hover:bg-[#e2e4e7] dark:hover:bg-[#4a5568] transition-colors cursor-pointer">
                            <Bell size={20} />
                            <span className="absolute top-2.5 right-2.5 size-2 bg-red-500 rounded-full border border-white dark:border-card-dark"></span>
                        </button>
                    )}

                    <button
                        onClick={toggleTheme}
                        className={isDetail
                            ? "flex items-center justify-center rounded-lg size-10 bg-[#f0f2f4] dark:bg-background-dark/50 text-slate-900 dark:text-white hover:bg-[#e2e4e7] dark:hover:bg-[#4a5568] transition-colors cursor-pointer"
                            : "p-2 text-[#617589] dark:text-gray-400 hover:bg-[#f0f2f4] dark:hover:bg-white/5 rounded-full transition-colors cursor-pointer"
                        }
                    >
                        {isDark ? (isDetail ? <Sun size={20} /> : <Sun size={24} />) : (isDetail ? <Moon size={20} /> : <Moon size={24} />)}
                    </button>

                    {!isDetail && (
                        <>
                            <div className="h-8 w-[1px] bg-[#f0f2f4] dark:bg-border-dark mx-2"></div>

                            {/* User Avatar / Login Button */}
                            <div className="relative" ref={menuRef}>
                                {user ? (
                                    <>
                                        <button
                                            onClick={() => setShowUserMenu(!showUserMenu)}
                                            className="flex items-center justify-center size-10 rounded-full bg-primary text-white font-bold text-sm hover:bg-primary/90 transition-colors cursor-pointer shadow-sm"
                                        >
                                            {user.email?.[0]?.toUpperCase() || 'U'}
                                        </button>

                                        {/* Dropdown Menu */}
                                        {showUserMenu && (
                                            <div className="absolute right-0 top-12 w-64 bg-white dark:bg-card-dark border border-[#f0f2f4] dark:border-border-dark rounded-xl shadow-xl z-50 overflow-hidden">
                                                <div className="p-4 border-b border-[#f0f2f4] dark:border-border-dark">
                                                    <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                                                        {user.full_name || 'User'}
                                                    </p>
                                                    <p className="text-xs text-slate-500 dark:text-gray-400 truncate">
                                                        {user.email}
                                                    </p>
                                                </div>
                                                <div className="p-2">
                                                    <button
                                                        onClick={() => {
                                                            logout();
                                                            setShowUserMenu(false);
                                                        }}
                                                        className="w-full flex items-center gap-3 px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/10 rounded-lg transition-colors"
                                                    >
                                                        <LogOut size={16} />
                                                        Log Out
                                                    </button>
                                                </div>
                                            </div>
                                        )}
                                    </>
                                ) : (
                                    <button
                                        onClick={openLogin}
                                        className="flex items-center justify-center size-10 rounded-full bg-[#f0f2f4] dark:bg-background-dark/50 text-slate-600 dark:text-gray-300 hover:bg-primary hover:text-white transition-colors cursor-pointer"
                                    >
                                        <User size={20} />
                                    </button>
                                )}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </header>
    );
};

export default Header;

