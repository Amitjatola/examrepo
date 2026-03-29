import React, { useState, useRef, useEffect, useCallback } from 'react';
import * as math from 'mathjs';

const GateCalculator = ({ onClose }) => {
    const [position, setPosition] = useState({ x: 100, y: 100 });
    const [isDragging, setIsDragging] = useState(false);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
    const calcRef = useRef(null);

    // Calculator State
    const [input, setInput] = useState('0');
    const [history, setHistory] = useState('');
    const [memory, setMemory] = useState(0);
    const [angleMode, setAngleMode] = useState('deg'); // 'deg' or 'rad'

    // Drag handlers
    const handleMouseDown = (e) => {
        setIsDragging(true);
        setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
    };

    const handleMouseMove = useCallback((e) => {
        if (!isDragging) return;
        setPosition({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    }, [isDragging, dragStart]);

    const handleMouseUp = useCallback(() => setIsDragging(false), []);

    useEffect(() => {
        if (isDragging) {
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
        }
        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging, handleMouseMove, handleMouseUp]);

    // Append value to input
    const append = (val) => {
        setInput(prev => (prev === '0' || prev === 'Error' ? val : prev + val));
    };

    const handleClear = () => { setInput('0'); setHistory(''); };

    const handleBackspace = () => {
        setInput(prev => (prev.length > 1 && prev !== 'Error' ? prev.slice(0, -1) : '0'));
    };

    // Evaluate logic — convert trig args to radians if angle mode is degrees
    const handleEvaluate = () => {
        try {
            let expr = input;

            if (angleMode === 'deg') {
                // Wrap trig function arguments with deg-to-rad conversion
                // e.g. sin(90) -> sin(90 * pi / 180)
                expr = expr.replace(
                    /\b(sin|cos|tan|asin|acos|atan|sinh|cosh|tanh|asinh|acosh|atanh)\(([^)]+)\)/g,
                    (match, fn, arg) => {
                        const inverseTrig = ['asin', 'acos', 'atan', 'asinh', 'acosh', 'atanh'].includes(fn);
                        if (inverseTrig) {
                            // inverse trig: compute normally, result is in degrees
                            return `(${fn}(${arg}) * 180 / pi)`;
                        }
                        // forward trig: convert arg from degrees to radians
                        return `${fn}((${arg}) * pi / 180)`;
                    }
                );
            }

            const rawRes = math.evaluate(expr);
            let formatted;
            if (typeof rawRes === 'number') {
                formatted = parseFloat(rawRes.toPrecision(12));
            } else if (rawRes && typeof rawRes.toString === 'function') {
                formatted = rawRes.toString();
            } else {
                formatted = String(rawRes);
            }
            setHistory(`${input} =`);
            setInput(String(formatted));
        } catch (e) {
            setHistory(input);
            setInput('Error');
        }
    };

    // Memory functions
    const getCurrentValue = () => {
        try {
            const val = math.evaluate(input);
            return typeof val === 'number' ? val : 0;
        } catch {
            return 0;
        }
    };

    const handleMS = () => setMemory(getCurrentValue());
    const handleMR = () => { if (memory !== 0) setInput(prev => (prev === '0' || prev === 'Error' ? String(memory) : prev + String(memory))); };
    const handleMC = () => setMemory(0);
    const handleMPlus = () => setMemory(prev => prev + getCurrentValue());
    const handleMMinus = () => setMemory(prev => prev - getCurrentValue());

    // Button renderer
    const btn = (label, onClick, colSpan = 1, bgColor = "bg-[#EFEFEF]", textColor = "text-black", font = "font-medium") => (
        <button
            onClick={onClick}
            className={`touch-manipulation ${bgColor} ${textColor} ${font} border border-gray-300 rounded-sm text-xs py-1.5 focus:outline-none hover:opacity-80 active:brightness-90 w-full shadow-sm flex items-center justify-center transition-all`}
            style={{ gridColumn: `span ${colSpan} / span ${colSpan}` }}
        >
            {label}
        </button>
    );

    return (
        <div
            ref={calcRef}
            className="fixed z-[100] w-[460px] bg-[#EAEAEA] border-4 border-[#3B82F6] rounded-sm shadow-2xl flex flex-col font-sans select-none"
            style={{ left: position.x, top: position.y }}
        >
            {/* Header */}
            <div
                className="bg-[#3B82F6] flex justify-between items-center px-2 py-1.5 cursor-move"
                onMouseDown={handleMouseDown}
            >
                <div className="text-white text-[13px] font-medium tracking-wide">Scientific Calculator with Complex Number</div>
                <div className="flex gap-1.5 text-white items-center shrink-0">
                    <button className="text-[11px] font-semibold bg-[#60A5FA] px-2 py-0.5 rounded-sm shadow">Help</button>
                    <button onClick={onClose} className="hover:bg-red-500 hover:text-white text-white px-1 py-0.5 rounded-sm transition-colors">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4"><path d="M18 6L6 18M6 6l12 12" /></svg>
                    </button>
                </div>
            </div>

            {/* Display Screen */}
            <div className="p-2 bg-[#E1E1E1] flex flex-col gap-1 border-b border-gray-300">
                <input type="text" readOnly className="w-full bg-white border border-gray-300 h-6 px-2 text-right text-xs text-gray-700 font-mono shadow-inner outline-none cursor-default" value={history} />
                <input type="text" readOnly className="w-full bg-white border border-gray-300 h-8 px-2 text-right text-base text-black font-semibold font-mono shadow-inner outline-none cursor-default" value={input} />
            </div>

            {/* Keyboard Panel */}
            <div className="p-2 bg-[#E1E1E1]">
                {/* Top Tools Row */}
                <div className="flex gap-2 items-center mb-2 justify-between">
                    <div className="flex gap-1 flex-1">
                        <button onClick={() => append('i')} className="bg-[#EFEFEF] border border-gray-300 rounded-sm text-xs pb-0.5 hover:bg-gray-300 w-8 shadow-sm font-serif italic text-center font-bold">i</button>
                        <button onClick={() => append(' mod ')} className="bg-[#EFEFEF] border border-gray-300 rounded-sm text-xs pb-0.5 hover:bg-gray-300 px-2 shadow-sm font-medium">mod</button>

                        {/* Deg/Rad Toggle — functional */}
                        <div className="flex items-center gap-1.5 border border-[#8cbcf5] bg-white rounded-sm px-1.5 py-0.5 shadow-sm">
                            <label className="flex items-center gap-1 text-[10px] font-medium text-black cursor-pointer leading-none">
                                <input
                                    type="radio"
                                    name="angle"
                                    value="deg"
                                    checked={angleMode === 'deg'}
                                    onChange={() => setAngleMode('deg')}
                                    className="h-2.5 w-2.5 accent-blue-600"
                                /> Deg
                            </label>
                            <label className="flex items-center gap-1 text-[10px] font-medium text-black cursor-pointer leading-none">
                                <input
                                    type="radio"
                                    name="angle"
                                    value="rad"
                                    checked={angleMode === 'rad'}
                                    onChange={() => setAngleMode('rad')}
                                    className="h-2.5 w-2.5 accent-blue-600"
                                /> Rad
                            </label>
                        </div>
                    </div>
                    <div className="flex gap-1">
                        <button onClick={handleMC} className="bg-[#EFEFEF] border border-gray-300 rounded-sm text-[11px] pb-0.5 px-2 hover:bg-gray-300 shadow-sm font-semibold">MC</button>
                        <button onClick={handleMR} className="bg-[#EFEFEF] border border-gray-300 rounded-sm text-[11px] pb-0.5 px-2 hover:bg-gray-300 shadow-sm font-semibold" title={`Memory: ${memory}`}>MR</button>
                        <button onClick={handleMS} className="bg-[#EFEFEF] border border-gray-300 rounded-sm text-[11px] pb-0.5 px-2 hover:bg-gray-300 shadow-sm font-semibold">MS</button>
                        <button onClick={handleMPlus} className="bg-[#EFEFEF] border border-gray-300 rounded-sm text-[11px] pb-0.5 px-2 hover:bg-gray-300 shadow-sm font-semibold">M+</button>
                        <button onClick={handleMMinus} className="bg-[#EFEFEF] border border-gray-300 rounded-sm text-[11px] pb-0.5 px-2 hover:bg-gray-300 shadow-sm font-semibold">M-</button>
                    </div>
                </div>

                {/* Main Scientific Grid */}
                <div className="grid grid-cols-11 gap-1 w-full">
                    {/* Row 1 */}
                    {btn("sinh", () => append('sinh('))}
                    {btn("cosh", () => append('cosh('))}
                    {btn("tanh", () => append('tanh('))}
                    {btn("Exp", () => append('exp('))}
                    {btn("(", () => append('('))}
                    {btn(")", () => append(')'))}
                    {btn("←", handleBackspace, 2, "bg-[#EF4444]", "text-white", "font-bold text-sm hover:bg-red-600")}
                    {btn("C", handleClear, 1, "bg-[#EF4444]", "text-white", "font-bold hover:bg-red-600")}
                    {btn("+/-", () => setInput(prev => prev.startsWith('-') ? prev.slice(1) : '-' + prev), 1, "bg-[#EF4444]", "text-white", "font-bold text-sm hover:bg-red-600")}
                    {btn("sqrt", () => append('sqrt('))}

                    {/* Row 2 */}
                    {btn(<span>sinh<sup>-1</sup></span>, () => append('asinh('))}
                    {btn(<span>cosh<sup>-1</sup></span>, () => append('acosh('))}
                    {btn(<span>tanh<sup>-1</sup></span>, () => append('atanh('))}
                    {btn(<span>log<sub>2</sub>x</span>, () => append('log2('))}
                    {btn("ln", () => append('log('))}
                    {btn("log", () => append('log10('))}
                    {btn("7", () => append('7'), 1, "bg-[#FAFAFA]", "text-black", "font-bold text-[13px] hover:bg-gray-200")}
                    {btn("8", () => append('8'), 1, "bg-[#FAFAFA]", "text-black", "font-bold text-[13px] hover:bg-gray-200")}
                    {btn("9", () => append('9'), 1, "bg-[#FAFAFA]", "text-black", "font-bold text-[13px] hover:bg-gray-200")}
                    {btn("/", () => append(' / '))}
                    {btn("%", () => append(' % '))}

                    {/* Row 3 */}
                    {btn("π", () => append('pi'), 1, "bg-[#EFEFEF]", "text-black", "font-serif italic font-bold text-[14px]")}
                    {btn("e", () => append('e'))}
                    {btn("n!", () => append('!'))}
                    {btn(<span>log<sub>y</sub>x</span>, () => append('log('))}
                    {btn(<span>e<sup>x</sup></span>, () => append('exp('))}
                    {btn(<span>10<sup>x</sup></span>, () => append('10^('))}
                    {btn("4", () => append('4'), 1, "bg-[#FAFAFA]", "text-black", "font-bold text-[13px] hover:bg-gray-200")}
                    {btn("5", () => append('5'), 1, "bg-[#FAFAFA]", "text-black", "font-bold text-[13px] hover:bg-gray-200")}
                    {btn("6", () => append('6'), 1, "bg-[#FAFAFA]", "text-black", "font-bold text-[13px] hover:bg-gray-200")}
                    {btn("*", () => append(' * '), 1, "bg-[#EFEFEF]", "text-black", "font-bold text-lg pb-1.5")}
                    {btn("1/x", () => setInput(prev => `1/(${prev})`))}

                    {/* Row 4 */}
                    {btn("sin", () => append('sin('))}
                    {btn("cos", () => append('cos('))}
                    {btn("tan", () => append('tan('))}
                    {btn(<span>x<sup>y</sup></span>, () => append('^'))}
                    {btn(<span>x<sup>3</sup></span>, () => append('^3'))}
                    {btn(<span>x<sup>2</sup></span>, () => append('^2'))}
                    {btn("1", () => append('1'), 1, "bg-[#FAFAFA]", "text-black", "font-bold text-[13px] hover:bg-gray-200")}
                    {btn("2", () => append('2'), 1, "bg-[#FAFAFA]", "text-black", "font-bold text-[13px] hover:bg-gray-200")}
                    {btn("3", () => append('3'), 1, "bg-[#FAFAFA]", "text-black", "font-bold text-[13px] hover:bg-gray-200")}
                    {btn("-", () => append(' - '), 1, "bg-[#EFEFEF]", "text-black", "font-bold text-lg pb-1.5")}
                    {/* Equal sign spans 2 rows */}
                    <button
                        onClick={handleEvaluate}
                        className="bg-[#10B981] text-white font-bold border border-[#059669] rounded-sm text-lg hover:bg-green-600 active:bg-green-700 shadow-sm flex flex-col items-center justify-center p-0 m-0 pb-1.5"
                        style={{ gridColumn: 'span 1 / span 1', gridRow: 'span 2 / span 2' }}
                    >
                        =
                    </button>

                    {/* Row 5 */}
                    {btn(<span>sin<sup>-1</sup></span>, () => append('asin('))}
                    {btn(<span>cos<sup>-1</sup></span>, () => append('acos('))}
                    {btn(<span>tan<sup>-1</sup></span>, () => append('atan('))}
                    {btn(<span><sup>y</sup>√x</span>, () => append('nthRoot('))}
                    {btn(<span><sup>3</sup>√x</span>, () => append('cbrt('))}
                    {btn("|x|", () => append('abs('))}
                    {btn("0", () => append('0'), 2, "bg-[#FAFAFA]", "text-black", "font-bold text-[13px] hover:bg-gray-200")}
                    {btn(".", () => append('.'), 1, "bg-[#FAFAFA]", "text-black", "font-bold text-xl pb-3 hover:bg-gray-200")}
                    {btn("+", () => append(' + '), 1, "bg-[#EFEFEF]", "text-black", "font-bold text-lg pb-1.5")}
                </div>
            </div>

            {/* Status Bar */}
            <div className="px-2 py-1 bg-[#D8D8D8] border-t border-gray-300 flex justify-between text-[10px] text-gray-600">
                <span>Mode: {angleMode === 'deg' ? 'Degrees' : 'Radians'}</span>
                <span>MEM: {memory !== 0 ? memory : '—'}</span>
            </div>
        </div>
    );
};

export default GateCalculator;
