```javascript
import React, { useState } from 'react';
import AuraRing from './AuraRing';
import PhysicsOverlay from './PhysicsOverlay';

const CapsulePortal = ({ data }) => {
    const [isHovered, setIsHovered] = useState(false);

    // Calculate position based on orbit and angle
    // Note: In a real 3D implementation (Three.js), this would be handled by the scene graph.
    // Here we simulate 2D orbit placement for the React prototype.

    const getOrbitRadius = (orbit) => {
        switch (orbit) {
            case 'inner': return 200;
            case 'middle': return 350;
            case 'outer': return 500;
            default: return 350;
        }
    };

    const radius = getOrbitRadius(data.orbit);
    const angleRad = (data.angle * Math.PI) / 180;

    // Center is (0,0) relative to the container center
    // We need to offset by 50% of screen, but since we are inside a flex center container,
    // absolute positioning works from the center if parent is relative.
    // Actually, standard absolute positioning is from top-left.
    // To make it easier, we'll use transform from center.

    const x = Math.cos(angleRad) * radius;
    const y = Math.sin(angleRad) * radius;

    return (
        <div
            className="capsule-portal"
            style={{
                transform: `translate(${ x }px, ${ y }px)`
            }}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <AuraRing status={data.status} />
            {isHovered ? (
                <PhysicsOverlay type="generic" />
            ) : (
                <div>{data.name}</div>
            )}
        </div>
    );
};

export default CapsulePortal;
```
