import React, { useState } from 'react';
import GateLoginScreen from './GateLoginScreen';
import GateInstructionsScreen from './GateInstructionsScreen';
import GateOtherInstructionsScreen from './GateOtherInstructionsScreen';
import CbtExamView from './CbtExamView';

const GateCbtWorkflow = ({ year, user, onBack }) => {
    // Determine the current user data
    const candidateName = user ? user.name || user.email.split('@')[0] : 'John Smith';
    const candidateImage = user?.picture || "https://ui-avatars.com/api/?name=John+Smith&background=random";

    // Workflow sequence: login -> instructions -> other_instructions -> exam
    const [step, setStep] = useState('login');

    if (step === 'login') {
        return (
            <GateLoginScreen 
                candidateName={candidateName}
                candidateImage={candidateImage}
                year={year}
                onNext={() => setStep('instructions')}
                onBack={onBack}
            />
        );
    }

    if (step === 'instructions') {
        return (
            <GateInstructionsScreen 
                candidateName={candidateName}
                candidateImage={candidateImage}
                onNext={() => setStep('other_instructions')}
                onExit={onBack}
            />
        );
    }

    if (step === 'other_instructions') {
        return (
            <GateOtherInstructionsScreen 
                candidateName={candidateName}
                candidateImage={candidateImage}
                onPrevious={() => setStep('instructions')}
                onStart={() => setStep('exam')}
                onExit={onBack}
            />
        );
    }

    if (step === 'exam') {
        return (
            <CbtExamView 
                year={year}
                onBack={onBack} // Exiting the exam goes back to the list
                user={user}
            />
        );
    }

    return null;
};

export default GateCbtWorkflow;
