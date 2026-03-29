import React, { useState } from 'react';

const GateOtherInstructionsScreen = ({ candidateName, candidateImage, onPrevious, onStart }) => {
    const [checked, setChecked] = useState(false);

    return (
        <div className="flex flex-col h-screen w-full bg-[#E5E5E5] font-sans selection:bg-blue-200">
            {/* Main Area */}
            <div className="flex flex-1 overflow-hidden">
                {/* Left Panel */}
                <div className="flex-1 flex flex-col bg-white overflow-hidden relative border-r-4 border-[#3c8dbd] m-2 mr-0 shadow-sm rounded-l">
                    {/* Header */}
                    <div className="bg-[#EFEFEF] py-2 px-6 border-b border-gray-300">
                        <div className="text-gray-800 font-bold text-lg">Other Important Instructions</div>
                    </div>
                    {/* Scrollable Content */}
                    <div className="flex-1 overflow-y-auto p-8 relative bg-white">
                        <div className="prose max-w-none text-gray-800 text-[15px] leading-relaxed">
                            <h4 className="font-bold underline mb-4 text-[#1E74B0]">Paper specific instructions</h4>
                            
                            <ol className="list-decimal pl-5 space-y-4 mb-8">
                                <li>The examination is of 3 hours duration. There are a total of 65 questions carrying 100 marks. The entire paper is divided into two sections: <strong>General Aptitude (GA)</strong> and <strong>Subject Specific</strong>.</li>
                                <li><strong>General Aptitude (GA):</strong> Questions Q.1 - Q.5 carry 1 mark each, and questions Q.6 - Q.10 carry 2 marks each.</li>
                                <li><strong>Subject Specific:</strong> Questions Q.11 - Q.35 carry 1 mark each, and questions Q.36 - Q.65 carry 2 marks each.</li>
                                <li><strong>Negative Marking:</strong> For 1-mark multiple-choice questions, 1/3 mark will be deducted for a wrong answer. For 2-mark multiple-choice questions, 2/3 mark will be deducted for a wrong answer. There is no negative marking for Numerical Answer Type (NAT) questions.</li>
                                <li>Calculators: An on-screen virtual calculator is available for use. Personal calculators, phones, or any other electronic devices are strictly prohibited.</li>
                                <li>Scribble pads will be provided for rough work. You must return the scribble pad to the invigilator at the end of the examination.</li>
                            </ol>

                            <div className="mt-8 border-t border-gray-300 pt-6">
                                <div className="flex items-center gap-4 mb-4">
                                    <span className="font-bold text-red-600">Choose your default language:</span>
                                    <select className="border border-gray-400 p-1 rounded min-w-[150px] bg-gray-50 focus:outline-none focus:border-blue-500">
                                        <option value="en">English</option>
                                    </select>
                                </div>
                                <p className="text-red-600 text-sm font-semibold mb-6">Please note all questions will appear in your default language. This language can be changed for a particular question later on.</p>
                            </div>
                        </div>
                    </div>
                    {/* Footer Nav with Declaration */}
                    <div className="bg-white border-t border-[#3c8dbd] p-4 flex flex-col gap-4 shrink-0 shadow-sm">
                        <label className="flex items-start gap-4 cursor-pointer">
                            <input 
                                type="checkbox" 
                                className="w-5 h-5 mt-1 border-gray-400 text-[#1E74B0] focus:ring-[#1E74B0] rounded-sm"
                                checked={checked}
                                onChange={(e) => setChecked(e.target.checked)}
                            />
                            <span className="text-sm font-medium text-gray-800 leading-relaxed text-justify">
                                I have read and understood the instructions. All computer hardware allotted to me are in proper working condition. I declare that I am not in possession of / not wearing / not carrying any prohibited gadget like mobile phone, bluetooth devices etc. / any prohibited material with me into the Examination Hall. I agree that in case of not adhering to the instructions, I shall be liable to be debarred from this Test and/or to disciplinary action, which may include ban from future Tests / Examinations.
                            </span>
                        </label>

                        <div className="flex justify-between items-center mt-2 border-t pt-4">
                            <button 
                                onClick={onPrevious}
                                className="px-6 py-2 text-sm font-bold bg-white text-gray-800 border border-gray-400 rounded shadow-sm hover:bg-gray-100 flex items-center"
                            >
                                &lt; Previous
                            </button>
                            <button 
                                onClick={onStart}
                                disabled={!checked}
                                className={`px-10 py-2.5 text-sm font-extrabold text-white border rounded shadow-md transition-colors 
                                    ${checked ? 'bg-[#337AB7] border-[#2E6DA4] hover:bg-[#286090]' : 'bg-gray-400 border-gray-400 cursor-not-allowed opacity-70'}`}
                            >
                                I am ready to begin
                            </button>
                        </div>
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

export default GateOtherInstructionsScreen;
