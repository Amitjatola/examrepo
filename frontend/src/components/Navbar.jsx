import React from 'react';
import { Sun, Moon, Focus, Minimize2 } from 'lucide-react';

const Navbar = ({ toggleTheme, theme, isZenMode, toggleZenMode }) => {
    return (
        <nav>
            <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                <a href="/" className="logo">AEROGATE</a>
                <div className="nav-actions" style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                        onClick={toggleZenMode}
                        className={`btn-icon ${isZenMode ? 'active' : ''}`}
                        title={isZenMode ? "Exit Zen Mode" : "Enter Zen Mode"}
                        aria-label="Toggle Zen Mode"
                    >
                        {isZenMode ? <Minimize2 size={20} /> : <Focus size={20} />}
                    </button>
                    <button
                        onClick={toggleTheme}
                        className="btn-icon"
                        title="Toggle Theme"
                        aria-label="Toggle Theme"
                    >
                        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                    </button>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
