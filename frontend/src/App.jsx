import React from 'react';
import MainContent from './components/MainContent';
import { AuthProvider } from './context/AuthContext';
import { GoogleOAuthProvider } from '@react-oauth/google';

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

function App() {
    return (
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID || 'dummy'}>
            <AuthProvider>
                <MainContent />
            </AuthProvider>
        </GoogleOAuthProvider>
    );
}

export default App;
