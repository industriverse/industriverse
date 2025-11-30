import React, { useState, useEffect } from 'react';
import { getStatus, getMetrics, getVaultItems } from '../utils/api_client';

const EmpeiriaPortal = () => {
  const [activeBeam, setActiveBeam] = useState(null);
  const [metrics, setMetrics] = useState({ entropy: 1.0, safety: 1.0, mastery_stage: "INIT" });
  const [vaultItems, setVaultItems] = useState([]);
  const [status, setStatus] = useState("CONNECTING...");

  useEffect(() => {
    const fetchData = async () => {
      const s = await getStatus();
      setStatus(s.status);

      const m = await getMetrics();
      setMetrics(m);

      const v = await getVaultItems();
      setVaultItems(v.items || []);
    };

    fetchData();
    const interval = setInterval(fetchData, 1000); // Poll every second
    return () => clearInterval(interval);
  }, []);

  // Dynamic Styles based on Entropy
  const pulseSpeed = metrics.entropy < 0.3 ? '0.5s' : '2s';
  const prismColor = metrics.entropy < 0.3 ? 'rgba(0, 255, 255, 0.3)' : 'rgba(255, 255, 255, 0.1)';

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
    statusLine: {
      position: 'absolute',
      top: '20px',
      right: '20px',
      fontSize: '12px',
      color: status === "RUNNING" ? '#00FF00' : '#FF0000'
    },
    metricsDisplay: {
      position: 'absolute',
      top: '20px',
      left: '20px',
      fontSize: '12px',
      textAlign: 'left'
    },
    prism: {
      width: '0',
      height: '0',
      borderLeft: '100px solid transparent',
      borderRight: '100px solid transparent',
      borderBottom: `173.2px solid ${prismColor} `,
      position: 'relative',
      cursor: 'pointer',
      transition: 'all 0.5s ease',
      filter: `drop - shadow(0 0 20px ${prismColor})`,
      animation: `pulse ${pulseSpeed} infinite alternate`
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
      color: '#D4AF37'
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
      textAlign: 'center',
      fontSize: '10px'
    }
  };

  return (
    <div style={styles.container}>
      <style>{`
@keyframes pulse {
          from { transform: scale(1); opacity: 0.8; }
          to { transform: scale(1.05); opacity: 1; }
}
`}</style>

      <div style={styles.statusLine}>SYSTEM STATUS: {status}</div>

      <div style={styles.metricsDisplay}>
        <div>ENTROPY: {metrics.entropy.toFixed(4)}</div>
        <div>SAFETY: {metrics.safety.toFixed(4)}</div>
        <div>STAGE: {metrics.mastery_stage}</div>
      </div>

      <div style={styles.title}>Empeiria Haus</div>

      {/* The Prism */}
      <div
        style={{
          ...styles.prism,
          borderBottomColor: activeBeam ? 'rgba(255, 255, 255, 0.3)' : prismColor
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
        {vaultItems.slice(0, 3).map((item, i) => (
          <div key={i} style={styles.artifact}>
            <div style={{ color: '#D4AF37', marginBottom: '10px' }}>DECLASSIFIED</div>
            <div>{item}</div>
          </div>
        ))}
        {vaultItems.length === 0 && <div style={{ opacity: 0.5 }}>VAULT LOCKED</div>}
      </div>

      <div style={{ position: 'absolute', bottom: '20px', fontSize: '10px', opacity: 0.5 }}>
        THE ARCHITECT'S VOID // EST. 2025
      </div>
    </div>
  );
};

export default EmpeiriaPortal;
