import React from 'react';

const GateInstructionsScreen = ({ candidateName, candidateImage, onNext }) => {
    return (
        <div className="flex flex-col h-screen w-full bg-[#E5E5E5] font-sans selection:bg-blue-200">
            {/* Main Area */}
            <div className="flex flex-1 overflow-hidden">
                {/* Left Panel */}
                <div className="flex-1 flex flex-col bg-white overflow-hidden relative border-r-4 border-[#3c8dbd] m-2 mr-0 shadow-sm rounded-l">
                    {/* Header */}
                    <div className="bg-[#EFEFEF] py-2 px-6 border-b border-gray-300">
                        <div className="text-gray-800 font-bold text-lg">General Instructions</div>
                    </div>
                    {/* Scrollable Content */}
                    <div className="flex-1 overflow-y-auto p-8 relative bg-white">
                        <div className="prose max-w-none text-gray-800 text-[15px] leading-relaxed">
                            <h4 className="font-bold underline mb-4 text-[#1E74B0]">Please read the instructions carefully</h4>
                            
                            <p className="font-bold mb-2">General Instructions:</p>
                            <ol className="list-decimal pl-5 space-y-4 mb-8">
                                <li>Total duration of examination is <strong>180 minutes</strong>.</li>
                                <li>The clock will be set at the server. The countdown timer in the top right corner of screen will display the remaining time available for you to complete the examination. When the timer reaches zero, the examination will end by itself. You will not be required to end or submit your examination.</li>
                                <li>The Question Palette displayed on the right side of screen will show the status of each question using one of the following symbols:
                                    <ul className="list-none pl-2 mt-3 space-y-3">
                                        <li className="flex items-center gap-3">
                                            <div className="relative flex items-center justify-center w-8 h-8">
                                                <svg viewBox="0 0 40 40" fill="none" className="absolute inset-0 drop-shadow-sm"><rect width="40" height="40" rx="4" fill="#EAEAEA" stroke="#CCCCCC" /></svg>
                                                <span className="relative text-black font-semibold text-xs">1</span>
                                            </div>
                                            <span>You have not visited the question yet.</span>
                                        </li>
                                        <li className="flex items-center gap-3">
                                            <div className="relative flex items-center justify-center w-8 h-8">
                                                <svg viewBox="0 0 40 40" fill="none" className="absolute inset-0 drop-shadow-md"><path d="M0 0 H40 V30 Q20 40 0 30 Z" fill="#E84142" /></svg>
                                                <span className="relative text-white font-semibold text-xs">2</span>
                                            </div>
                                            <span>You have not answered the question.</span>
                                        </li>
                                        <li className="flex items-center gap-3">
                                            <div className="relative flex items-center justify-center w-8 h-8">
                                                <svg viewBox="0 0 40 40" fill="none" className="absolute inset-0 drop-shadow-md"><path d="M0 10 Q20 0 40 10 V40 H0 Z" fill="#29A645" /></svg>
                                                <span className="relative text-white font-semibold text-xs">3</span>
                                            </div>
                                            <span>You have answered the question.</span>
                                        </li>
                                        <li className="flex items-center gap-3">
                                            <div className="relative flex items-center justify-center w-8 h-8">
                                                <svg viewBox="0 0 40 40" fill="none" className="absolute inset-0 drop-shadow-md"><circle cx="20" cy="20" r="20" fill="#75529A" /></svg>
                                                <span className="relative text-white font-semibold text-xs">4</span>
                                            </div>
                                            <span>You have NOT answered the question, but have marked the question for review.</span>
                                        </li>
                                        <li className="flex items-center gap-3">
                                            <div className="relative flex items-center justify-center w-8 h-8">
                                                <svg viewBox="0 0 40 40" fill="none" className="absolute inset-0 drop-shadow-md"><circle cx="20" cy="20" r="20" fill="#75529A" /><circle cx="32" cy="32" r="6" fill="#29A645" stroke="white" strokeWidth="1"/></svg>
                                                <span className="relative text-white font-semibold text-xs">5</span>
                                            </div>
                                            <span>The question(s) "Answered and Marked for Review" will be considered for evaluation.</span>
                                        </li>
                                    </ul>
                                </li>
                                <li>You can click on the "&gt;" arrow which appears to the left of question palette to collapse the question palette thereby maximizing the question window. To view the question palette again, you can click on "&lt;" which appears on the right side of question window.</li>
                            </ol>

                            <p className="font-bold mb-2">Navigating to a Question:</p>
                            <ol className="list-decimal pl-5 space-y-2 mb-8" start="5">
                                <li>To answer a question, do the following:
                                    <ol className="list-alpha pl-5 space-y-2 mt-2">
                                        <li>Click on the question number in the Question Palette at the right of your screen to go to that numbered question directly. Note that using this option does NOT save your answer to the current question.</li>
                                        <li>Click on <strong>Save & Next</strong> to save your answer for the current question and then go to the next question.</li>
                                        <li>Click on <strong>Mark for Review & Next</strong> to save your answer for the current question, mark it for review, and then go to the next question.</li>
                                    </ol>
                                </li>
                            </ol>

                            <p className="font-bold mb-2">Answering a Question:</p>
                            <ol className="list-decimal pl-5 space-y-2" start="6">
                                <li>Procedure for answering a multiple choice type question:
                                    <ol className="list-alpha pl-5 space-y-2 mt-2">
                                        <li>To select your answer, click on the button of one of the options.</li>
                                        <li>To deselect your chosen answer, click on the button of the chosen option again or click on the <strong>Clear Response</strong> button.</li>
                                        <li>To change your chosen answer, click on the button of another option.</li>
                                        <li>To save your answer, you MUST click on the <strong>Save & Next</strong> button.</li>
                                    </ol>
                                </li>
                            </ol>
                        </div>
                    </div>
                    {/* Footer Nav */}
                    <div className="bg-[#EFEFEF] border-t border-gray-300 p-3 flex justify-end shrink-0 shadow-sm">
                        <button 
                            onClick={onNext}
                            className="px-6 py-2 text-sm font-bold bg-[#1E74B0] text-white border border-[#165A8A] rounded shadow-sm hover:bg-[#165A8A] flex items-center"
                        >
                            Next &gt;
                        </button>
                    </div>
                </div>

                {/* Right Panel */}
                <div className="w-72 flex flex-col bg-[#cbe3f0] shrink-0 m-2 ml-0 shadow-sm rounded-r border border-gray-300">
                    <div className="bg-white p-4 flex flex-col items-center gap-4 shrink-0 shadow-sm border-b rounded-tr">
                         <div className="w-24 h-28 border border-gray-300 shadow-inner overflow-hidden mb-2">
                            <img src={candidateImage} alt="Candidate" className="w-full h-full object-cover" />
                        </div>
                        <div className="text-center font-bold text-gray-800 text-lg w-full truncate px-2">{candidateName}</div>
                    </div>
                </div>
            </div>
            {/* Version Footer */}
            <div className="bg-[#5C728F] text-white text-center py-1.5 text-xs font-medium">
                Version 17.05.21
            </div>
        </div>
    );
};

export default GateInstructionsScreen;
