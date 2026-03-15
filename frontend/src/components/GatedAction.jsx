import React from 'react';
import { useAuth } from '../context/AuthContext';

/**
 * GatedAction — wraps interactive elements that require authentication.
 * 
 * For guests: intercepts the click and opens the AuthModal with a contextual message.
 * For free users needing premium: shows upgrade prompt.
 * For authorized users: passes the click through normally.
 * 
 * Usage:
 *   <GatedAction message="Sign in to reply to this discussion">
 *     <button onClick={handleReply}>Reply</button>
 *   </GatedAction>
 */
const GatedAction = ({ children, message = "Sign in to continue", requiredTier = 'free' }) => {
    const { user, isPremium, requireAuth } = useAuth();

    const handleClick = (e) => {
        // If user is not logged in, gate it
        if (!user) {
            e.preventDefault();
            e.stopPropagation();
            requireAuth(message);
            return;
        }

        // If premium is required but user is not premium
        if (requiredTier === 'premium' && !isPremium) {
            e.preventDefault();
            e.stopPropagation();
            requireAuth("Upgrade to Premium to access this feature");
            return;
        }

        // Otherwise, let the click pass through normally
    };

    return (
        <div onClick={handleClick} className="contents">
            {children}
        </div>
    );
};

export default GatedAction;
