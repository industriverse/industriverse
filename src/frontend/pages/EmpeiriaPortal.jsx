import React, { useState } from 'react';

const EmpeiriaPortal = () => {
    const [activeBeam, setActiveBeam] = useState(null); // 'industriverse' | 'thermodynasty' | null

    const styles = {
        container: {
            width: '100vw',
            height: '100vh',
            backgroundColor: '#000000',
            color: '#E0E0E0',
            fontFamily: '"JetBrains Mono", monospace',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
            position: 'relative'
        },
        prism: {
            width: '0',
            height: '0',
            borderLeft: '100px solid transparent',
            borderRight: '100px solid transparent',
            borderBottom: '173.2px solid rgba(255, 255, 255, 0.1)',
            position: 'relative',
            cursor: 'pointer',
            transition: 'all 0.5s ease',
            filter: 'drop-shadow(0 0 20px rgba(255,255,255,0.2))'
        },
        beam: {
            position: 'absolute',
            top: '50%',
            left: '50%',
            width: '400px',
            height: '2px',
            transformOrigin: 'left center',
            transition: 'all 0.5s ease',
            opacity: 0.6
        },
        industriverseBeam: {
            background: 'linear-gradient(90deg, rgba(255,255,255,0.8), #00FFFF)',
            transform: 'rotate(-30deg)',
            boxShadow: '0 0 15px #00FFFF'
        },
        thermodynastyBeam: {
            background: 'linear-gradient(90deg, rgba(255,255,255,0.8), #FF4500)',
            transform: 'rotate(30deg)',
            boxShadow: '0 0 15px #FF4500'
        },
        title: {
            position: 'absolute',
            top: '10%',
            letterSpacing: '10px',
            fontSize: '24px',
            textTransform: 'uppercase',
            color: '#D4AF37' // Stellar Gold
        },
        vault: {
            position: 'absolute',
            bottom: '10%',
            display: 'flex',
            gap: '40px',
            opacity: activeBeam ? 1 : 0.3,
            transition: 'opacity 0.5s'
        },
        artifact: {
            border: '1px solid rgba(255,255,255,0.2)',
            padding: '20px',
            width: '200px',
            textAlign: 'center'
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.title}>Empeiria Haus</div>

            {/* The Prism */}
            <div
                style={{
                    ...styles.prism,
                    borderBottomColor: activeBeam ? 'rgba(255, 255, 255, 0.3)' : 'rgba(255, 255, 255, 0.1)'
                }}
                onMouseEnter={() => setActiveBeam('all')}
                onMouseLeave={() => setActiveBeam(null)}
            >
                {/* Refracted Beams */}
                <div style={{
                    ...styles.beam,
                    ...styles.industriverseBeam,
                    width: activeBeam ? '500px' : '0px'
                }}>
                    <div style={{ position: 'absolute', right: '-120px', top: '-10px', color: '#00FFFF' }}>
                        INDUSTRIVERSE
                    </div>
                </div>

                <div style={{
                    ...styles.beam,
                    ...styles.thermodynastyBeam,
                    width: activeBeam ? '500px' : '0px'
                }}>
                    <div style={{ position: 'absolute', right: '-130px', top: '-10px', color: '#FF4500' }}>
                        THERMODYNASTY
                    </div>
                </div>
            </div>

            {/* The Project Vault */}
            <div style={styles.vault}>
                <div style={styles.artifact}>
                    <div style={{ color: '#D4AF37', marginBottom: '10px' }}>VOL. 1</div>
                    <div>THERMODYNAMIC AI</div>
                </div>
                <div style={styles.artifact}>
                    <div style={{ color: '#D4AF37', marginBottom: '10px' }}>VOL. 2</div>
                    <div>EGOCENTRIC ROBOTICS</div>
                </div>
                <div style={styles.artifact}>
                    <div style={{ color: '#D4AF37', marginBottom: '10px' }}>VOL. 3</div>
                    <div>ZK MANUFACTURING</div>
                </div>
            </div>

            <div style={{ position: 'absolute', bottom: '20px', fontSize: '10px', opacity: 0.5 }}>
                THE ARCHITECT'S VOID // EST. 2025
            </div>
        </div>
    );
};

export default EmpeiriaPortal;
