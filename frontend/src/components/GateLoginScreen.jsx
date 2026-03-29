import React from 'react';
import { User, Lock } from 'lucide-react';

const GateLoginScreen = ({ candidateName, candidateImage, year, onNext }) => {
    return (
        <div className="flex flex-col h-screen w-full bg-[#E5E5E5] font-sans selection:bg-blue-200">
            {/* Top White Banner */}
            <div className="bg-white px-6 py-2 flex items-center justify-between border-b">
                <div className="flex items-center gap-4">
                    <img src="/gate-logo-placeholder.png" alt="GATE Logo" className="h-12 w-auto object-contain opacity-70" 
                         onError={(e) => { e.target.style.display='none'; e.target.nextSibling.style.display='block'; }}/>
                    <div className="hidden font-bold text-[#4B0082] text-xl">GATE</div>
                </div>
                <div className="text-center font-bold text-[#6a359c] text-lg lg:text-xl tracking-tight hidden md:block uppercase">
                    GRADUATE APTITUDE TEST IN ENGINEERING (GATE {year || '2026'})
                    <div className="text-[#3b82f6] text-xs lg:text-sm font-semibold tracking-normal mt-0.5">Organizing Institute : INDIAN INSTITUTE OF TECHNOLOGY GUWAHATI</div>
                </div>
                <div className="flex items-center">
                   <div className="h-12 w-12 rounded-full border-2 border-orange-400 flex items-center justify-center bg-blue-50 text-blue-900 font-bold text-xs opacity-70">
                       IITG
                   </div>
                </div>
            </div>

            {/* Grey System Band */}
            <div className="bg-[#717171] px-6 py-3 flex justify-between items-stretch shadow-md">
                {/* Left Side: System Info */}
                <div className="flex flex-col justify-between">
                    <div>
                        <div className="text-white font-semibold text-lg md:text-xl">System Name :</div>
                        <div className="text-[#F1E00D] font-bold text-4xl md:text-5xl tracking-wider leading-none mt-1">C001</div>
                    </div>
                    <div className="text-white text-sm mt-4 font-medium opacity-90 max-w-xl">
                        Kindly contact the invigilator if there are any discrepancies in the Name and Photograph displayed on the screen or if the photograph is not yours
                    </div>
                </div>

                {/* Right Side: Candidate Info & Photo */}
                <div className="flex gap-4">
                    <div className="flex flex-col text-right justify-center">
                        <div className="text-white font-semibold text-lg">Candidate Name :</div>
                        <div className="text-[#F1E00D] font-bold text-2xl md:text-3xl leading-tight mb-2">{candidateName}</div>
                        <div className="text-white text-base">Subject : <span className="text-[#F1E00D] font-bold">Mock Exam</span></div>
                    </div>
                    <div className="border border-black bg-white p-0.5 w-24 h-28 md:w-28 md:h-32 shadow-lg shrink-0 flex items-center justify-center overflow-hidden">
                        <img src={candidateImage} alt="Candidate" className="w-full h-full object-cover" />
                    </div>
                </div>
            </div>

            {/* Main Login Area */}
            <div className="flex-1 flex justify-center items-center">
                <div className="bg-[#EAEAEA] border border-[#CCCCCC] rounded shadow-sm w-full max-w-sm flex flex-col">
                    <div className="bg-[#D1D1D1] px-4 py-2 text-gray-800 font-bold text-sm border-b border-[#B8B8B8] rounded-t">
                        Login
                    </div>
                    <div className="p-6 bg-[#F4F4F4]">
                        <div className="space-y-4">
                            <div className="flex items-center">
                                <div className="bg-[#DCDCDC] border border-[#B3B3B3] border-r-0 p-2 text-gray-600 rounded-l">
                                    <User size={20} />
                                </div>
                                <input 
                                    type="text" 
                                    defaultValue="11111" 
                                    className="flex-1 border border-[#B3B3B3] p-2 text-gray-700 focus:outline-none"
                                    disabled
                                />
                                <div className="bg-[#DCDCDC] border border-[#B3B3B3] border-l-0 p-2 text-gray-600 rounded-r flex cursor-not-allowed">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M6 14h.01M18 14h.01M10 14h4"/></svg>
                                </div>
                            </div>

                            <div className="flex items-center">
                                <div className="bg-[#DCDCDC] border border-[#B3B3B3] border-r-0 p-2 text-gray-600 rounded-l">
                                    <Lock size={20} />
                                </div>
                                <input 
                                    type="password" 
                                    defaultValue="mockpassword" 
                                    className="flex-1 border border-[#B3B3B3] p-2 text-gray-700 text-2xl tracking-[0.2em] focus:outline-none"
                                    disabled
                                />
                                <div className="bg-[#DCDCDC] border border-[#B3B3B3] border-l-0 p-2 text-gray-600 rounded-r flex cursor-not-allowed">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M6 14h.01M18 14h.01M10 14h4"/></svg>
                                </div>
                            </div>

                            <button 
                                onClick={onNext}
                                className="w-full mt-6 bg-[#2FA6EB] hover:bg-[#1E74B0] text-white font-bold py-2.5 rounded shadow transition-colors"
                            >
                                Sign In
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="bg-[#5C728F] text-white text-center py-1.5 text-xs font-medium">
                Version 17.05.21
            </div>
        </div>
    );
};

export default GateLoginScreen;
