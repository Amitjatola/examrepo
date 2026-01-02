import React, { useState, useEffect, useRef } from 'react';
import { Search, Sparkles, CornerDownLeft } from 'lucide-react';
import { api } from '../utils/api';

const SearchBox = ({ onSearch, initialValue = '' }) => {
    const [inputValue, setInputValue] = useState(initialValue);
    const [suggestions, setSuggestions] = useState([]);
    const [activeIndex, setActiveIndex] = useState(-1);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const wrapperRef = useRef(null);
    const isSelection = useRef(false);

    // Debounce suggestion fetching
    useEffect(() => {
        const fetchSuggestions = async () => {
            // If this update was caused by a selection, ignore it
            if (isSelection.current) {
                isSelection.current = false;
                return;
            }

            if (inputValue.length < 2) {
                setSuggestions([]);
                return;
            }
            try {
                const results = await api.getSuggestions(inputValue, 5);
                setSuggestions(results);
                setShowSuggestions(true);
            } catch (error) {
                console.error("Suggestion fetch error:", error);
            }
        };

        const timeoutId = setTimeout(fetchSuggestions, 300);
        return () => clearTimeout(timeoutId);
    }, [inputValue]);

    // Handle outside click to close dropdown
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                setShowSuggestions(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleKeyDown = (e) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setActiveIndex(prev => (prev < suggestions.length - 1 ? prev + 1 : prev));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setActiveIndex(prev => (prev > 0 ? prev - 1 : -1));
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (activeIndex >= 0 && suggestions[activeIndex]) {
                selectSuggestion(suggestions[activeIndex]);
            } else {
                onSearch(inputValue);
                setShowSuggestions(false);
            }
        } else if (e.key === 'Escape') {
            setShowSuggestions(false);
        }
    };

    const selectSuggestion = (suggestion) => {
        isSelection.current = true;
        setInputValue(suggestion);
        onSearch(suggestion);
        setShowSuggestions(false);
        setSuggestions([]);
    };

    return (
        <div className="search-container" ref={wrapperRef}>
            <div className="search-icon">
                <Search size={20} />
            </div>
            <input
                type="text"
                className="search-input"
                placeholder="Type a concept (e.g. 'Eigenvalues', 'Boundary Layer')..."
                value={inputValue}
                onChange={(e) => {
                    setInputValue(e.target.value);
                    setActiveIndex(-1);
                }}
                onKeyDown={handleKeyDown}
                onFocus={() => inputValue.length >= 2 && setShowSuggestions(true)}
            />

            {showSuggestions && suggestions.length > 0 && (
                <div className="search-dropdown">
                    {suggestions.map((suggestion, index) => (
                        <div
                            key={index}
                            className={`suggestion-item ${index === activeIndex ? 'active' : ''}`}
                            onClick={() => selectSuggestion(suggestion)}
                            onMouseEnter={() => setActiveIndex(index)}
                        >
                            <Sparkles size={14} className="suggestion-icon" />
                            <span>{suggestion}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default SearchBox;
