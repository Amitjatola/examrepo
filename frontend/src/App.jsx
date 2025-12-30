import React from 'react';
import MainContent from './components/MainContent';
import { AuthProvider } from './context/AuthContext';

function App() {
    return (
        <AuthProvider>
            <MainContent />
        </AuthProvider>
    );
}

export default App;
