import React from 'react';

const IntentionStar = ({ intent }) => {
    return (
        <div className="intention-star" title="Intention Core">
            <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                textAlign: 'center',
                pointerEvents: 'none'
            }}>
                <div style={{ fontSize: '10px', fontWeight: 'bold', color: '#111' }}>CORE</div>
            </div>
        </div>
    );
};

export default IntentionStar;
