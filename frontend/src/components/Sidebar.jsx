import React from 'react';
import { LayoutDashboard, BookOpen, Lightbulb, History, GraduationCap, LogOut, LogIn, Tag, Info, X, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar = ({ activeTab, onTabChange, onOpen = () => { }, isOpen = true, onLogoClick, onClose }) => {
    const { user, openLogin, logout } = useAuth();

    // Menu items change based on login status
    const getMenuItems = () => {
        if (user) {
            // Logged in: Show all features
            return [
                { id: 'home', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
                { id: 'year_select', label: 'Practice by Year', icon: <BookOpen size={20} /> },
                { id: 'concepts', label: 'Browse by Syllabus', icon: <Lightbulb size={20} /> },
                { id: 'history', label: 'History', icon: <History size={20} /> },
                { type: 'label', label: 'ACCOUNT' },
                { id: 'premium', label: 'Upgrade / Premium', icon: <Sparkles size={20} className="text-blue-500" /> },
            ];
        } else {
            // Not logged in: Show limited browse options
            return [
                { id: 'year_select', label: 'Practice by Year', icon: <BookOpen size={20} /> },
                { id: 'concepts', label: 'Browse Concepts', icon: <Lightbulb size={20} /> },
                { type: 'divider' },
                { id: 'pricing', label: 'Pricing', icon: <Tag size={20} /> },
                { id: 'about', label: 'About Platform', icon: <Info size={20} /> },
            ];
        }
    };

    const menuItems = getMenuItems();

    if (!isOpen) {
        return (
            <div className="fixed inset-y-0 left-0 z-20 w-0 transition-all duration-300"></div>
        );
    }

    return (
        <>
            {/* Mobile Backdrop */}
            <div
                className="fixed inset-0 bg-black/50 z-20 lg:hidden transition-opacity"
                onClick={onClose}
                aria-hidden="true"
            />

            <aside className="fixed inset-y-0 left-0 bg-white dark:bg-[#101323] border-r border-[#f0f2f4] dark:border-border-dark flex flex-col justify-between z-30 w-72 transition-transform duration-300 shadow-xl lg:shadow-none">
                <div className="flex flex-col p-6 flex-1 relative">
                    {/* Header: Logo and Close Button */}
                    <div className="flex items-center justify-between mb-8">
                        <button
                            onClick={onLogoClick}
                            className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity text-left"
                        >
                            <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center text-white">
                                <GraduationCap size={20} />
                            </div>
                            <div>
                                <h1 className="text-slate-900 dark:text-white text-base font-bold leading-tight font-display">ExamPrep</h1>
                                <p className="text-slate-400 text-xs font-normal">Master your field</p>
                            </div>
                        </button>

                        {/* Mobile Close Button */}
                        <button
                            onClick={onClose}
                            className="lg:hidden p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
                        >
                            <X size={20} />
                        </button>
                    </div>

                    {/* Nav Items */}
                    <nav className="flex flex-col gap-1">
                        {menuItems.map((item, index) => {
                            if (item.type === 'divider') {
                                return <div key={`divider-${index}`} className="h-px bg-slate-200 dark:bg-border-dark my-2 mx-3"></div>;
                            }
                            if (item.type === 'label') {
                                return (
                                    <div key={`label-${index}`} className="px-3 mt-4 mb-2">
                                        <p className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">{item.label}</p>
                                    </div>
                                );
                            }

                            const isActive = activeTab === item.id;
                            return (
                                <button
                                    key={item.id}
                                    onClick={() => onTabChange(item.id)}
                                    className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group text-left w-full cursor-pointer
                                        ${isActive
                                            ? 'bg-primary/10 text-primary'
                                            : 'text-slate-400 hover:text-slate-100 hover:bg-white/5'
                                        }`}
                                >
                                    <span className={`transition-colors ${isActive ? 'text-primary' : 'text-slate-500 dark:text-slate-400 group-hover:text-slate-100'}`}>
                                        {item.icon}
                                    </span>
                                    <span className={`text-sm font-medium ${isActive ? 'text-primary' : 'text-slate-900 dark:text-slate-300'}`}>
                                        {item.label}
                                    </span>
                                </button>
                            );
                        })}
                    </nav>
                </div>

                {/* Bottom Section */}
                <div className="p-4 border-t border-slate-200 dark:border-border-dark">
                    <div className="flex flex-col gap-2">
                        {user ? (
                            <>

                                {/* User Profile Section */}
                                <div className="mt-2 pt-2 border-t border-slate-200 dark:border-border-dark/50">
                                    <div className="flex items-center gap-3 px-3 py-2 rounded-lg transition-colors mb-1">
                                        <div className="size-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-sm">
                                            {user.email[0].toUpperCase()}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-slate-900 dark:text-gray-100 truncate">
                                                {user.full_name || 'User'}
                                            </p>
                                            <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
                                                {user.email}
                                            </p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={logout}
                                        className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/10 text-red-600 dark:text-red-400 transition-colors w-full text-left cursor-pointer mt-1"
                                    >
                                        <LogOut size={18} />
                                        <span className="text-sm font-medium">Log Out</span>
                                    </button>
                                </div>
                            </>
                        ) : (
                            <button
                                onClick={openLogin}
                                className="flex w-full cursor-pointer items-center justify-center rounded-lg h-10 px-4 bg-primary hover:bg-primary/90 transition-colors text-white text-sm font-bold shadow-lg shadow-primary/20"
                            >
                                <span>Log In / Sign Up</span>
                            </button>
                        )}
                    </div>
                </div>
            </aside>
        </>
    );
};

export default Sidebar;
