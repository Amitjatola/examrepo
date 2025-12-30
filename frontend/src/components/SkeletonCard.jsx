
import React from 'react';

const SkeletonCard = () => {
    return (
        <div className="question-card skeleton-card">
            <div className="question-header">
                <div className="skeleton-line badge-skeleton"></div>
                <div className="skeleton-line badge-skeleton"></div>
            </div>

            <div className="question-body">
                <div className="skeleton-line text-skeleton" style={{ width: '100%' }}></div>
                <div className="skeleton-line text-skeleton" style={{ width: '90%' }}></div>
                <div className="skeleton-line text-skeleton" style={{ width: '95%' }}></div>
                <div className="skeleton-line text-skeleton" style={{ width: '60%' }}></div>

                <div className="options-grid" style={{ marginTop: '2rem' }}>
                    <div className="skeleton-line option-skeleton"></div>
                    <div className="skeleton-line option-skeleton"></div>
                    <div className="skeleton-line option-skeleton"></div>
                    <div className="skeleton-line option-skeleton"></div>
                </div>
            </div>

            <div className="question-footer">
                <div className="skeleton-line tag-skeleton"></div>
                <div className="skeleton-line btn-skeleton"></div>
            </div>
        </div>
    );
};

export default SkeletonCard;
