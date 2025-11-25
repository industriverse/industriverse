# TouchDesigner Project Template for Capsule Pins

**Generative data visualization for factory metrics → real-time art**

---

## 🎨 **Project Overview**

This TouchDesigner project transforms factory metrics into mesmerizing generative visualizations:

- **Temperature** → Color gradient (blue → red)
- **Pressure** → Particle density
- **Vibration** → Displacement noise
- **Production rate** → Animation speed
- **Noise** → Audio-reactive visuals

---

## 📊 **Network Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│ Capsule Gateway (WebSocket Server)                             │
│ - Receives factory sensor data                                  │
│ - Broadcasts capsule updates                                    │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ TouchDesigner Bridge (Python WebSocket)                        │
│ - Receives capsule updates                                      │
│ - Sends to TouchDesigner via OSC/WebSocket                      │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ TouchDesigner (Generative Art Engine)                          │
│ ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│ │ Data Input  │  │ Procedural   │  │ Real-Time Rendering  │   │
│ │ (OSC/WS)    │  │ Generation   │  │ (60 fps)             │   │
│ └─────────────┘  └──────────────┘  └──────────────────────┘   │
│ ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│ │ Audio       │  │ Geometry     │  │ Texture Export       │   │
│ │ Reactive    │  │ Export       │  │ (.png/.jpg)          │   │
│ └─────────────┘  └──────────────┘  └──────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Web Export (Three.js)                                           │
│ - Geometry (.obj/.fbx)                                          │
│ - Textures (.png/.jpg)                                          │
│ - Animation data (JSON)                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 **TouchDesigner Network Setup**

### **1. Data Input (OSC In / WebSocket In)**

**OSC In CHOP:**
- Network Port: `9000`
- Protocol: `OSC`
- Channels:
  - `temperature` (0-100)
  - `pressure` (0-100)
  - `vibration` (0-100)
  - `production_rate` (0-100)
  - `noise` (0-100)

**WebSocket DAT:**
- Server Address: `ws://localhost:9980`
- Protocol: `JSON`
- Receive capsule updates

---

### **2. Procedural Geometry Generation**

#### **Critical Status: Pulsing Sphere with Spikes**

```python
# In Geometry COMP
import numpy as np

# Get metrics
temperature = op('osc_in')['temperature']
vibration = op('osc_in')['vibration']

# Generate icosphere
geo = op('icosphere1')

# Add spikes based on vibration
for point in geo.points:
    normal = point.normal
    spike_length = 0.05 + (vibration / 100) * 0.1
    point.P += normal * spike_length

# Pulse scale based on vibration
scale = 1 + abs(np.sin(absTime.seconds * vibration / 10)) * 0.3
op('transform1').par.scale = scale
```

#### **Warning Status: Rotating Cube with Glow**

```python
# In Geometry COMP
pressure = op('osc_in')['pressure']

# Rotate based on production rate
production_rate = op('osc_in')['production_rate']
rotation_speed = 30 + (production_rate / 100) * 90  # 30-120 deg/sec
op('transform1').par.rx = absTime.seconds * rotation_speed

# Glow intensity based on pressure
glow_intensity = 0.3 + (pressure / 100) * 0.7
op('constant1').par.colorr = 1
op('constant1').par.colorg = 0.67
op('constant1').par.colorb = 0.2
op('constant1').par.alpha = glow_intensity
```

#### **Active Status: Smooth Torus with Flow**

```python
# In Geometry COMP
production_rate = op('osc_in')['production_rate']

# Flow rotation
rotation_speed = 20 + (production_rate / 100) * 40  # 20-60 deg/sec
op('transform1').par.ry = absTime.seconds * rotation_speed
op('transform1').par.rx = np.sin(absTime.seconds * 0.5) * 20
```

---

### **3. Material Generation**

#### **Temperature-Based Color Gradient**

```python
# In Constant MAT
temperature = op('osc_in')['temperature']

# Map temperature to HSL color
hue = 0.6 - (temperature / 100) * 0.6  # Blue (0.6) to Red (0)
saturation = 1.0
lightness = 0.5

# Convert HSL to RGB
import colorsys
r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)

op('constant1').par.colorr = r
op('constant1').par.colorg = g
op('constant1').par.colorb = b
```

#### **Pressure-Based Glow**

```python
# In Constant MAT
pressure = op('osc_in')['pressure']

# Map pressure to emissive intensity
emissive_intensity = 0.3 + (pressure / 100) * 0.7

op('constant1').par.emit = emissive_intensity
```

---

### **4. Audio Reactive Visualization**

#### **Audio In CHOP**

```python
# In Audio Device In CHOP
# Device: Default microphone
# Sample Rate: 44100 Hz
# Channels: Mono

# Audio Analysis CHOP
audio_in = op('audioin1')
audio_analyzer = op('audioanalyzer1')

# Get frequency bands
bass = audio_analyzer['bass']      # 20-250 Hz
mid = audio_analyzer['mid']        # 250-2000 Hz
treble = audio_analyzer['treble']  # 2000-20000 Hz

# Map to visual parameters
scale = 1 + (bass / 255) * 0.5
emissive = 0.5 + (mid / 255) * 0.5
rotation_speed = 30 + (treble / 255) * 90
```

#### **Audio-Reactive Particle System**

```python
# In Particle SOP
audio_in = op('audioin1')
audio_analyzer = op('audioanalyzer1')

# Particle emission rate based on audio level
average_level = audio_analyzer['average']
emission_rate = 10 + (average_level / 255) * 90  # 10-100 particles/sec

op('particle1').par.birthrate = emission_rate

# Particle velocity based on bass
bass = audio_analyzer['bass']
velocity = 0.5 + (bass / 255) * 2  # 0.5-2.5 m/s

op('particle1').par.velocityvar = velocity
```

---

### **5. Texture Export**

#### **Render TOP → Export**

```python
# In Render TOP
render_top = op('render1')

# Export texture every frame
def onFrameEnd(frame):
    capsule_id = op('constant1').par.value0  # Get capsule ID
    export_path = f"exports/{capsule_id}_diffuse.png"
    
    render_top.save(export_path)
    
    # Notify WebSocket clients
    op('websocket_out').sendText(json.dumps({
        'type': 'texture_update',
        'capsule_id': capsule_id,
        'texture_url': f"http://localhost:8080/{export_path}"
    }))
```

---

### **6. Geometry Export**

#### **Geometry COMP → OBJ Export**

```python
# In Geometry COMP
geo = op('geo1')

def onFrameEnd(frame):
    capsule_id = op('constant1').par.value0  # Get capsule ID
    export_path = f"exports/{capsule_id}.obj"
    
    # Export geometry
    geo.save(export_path)
    
    # Notify WebSocket clients
    op('websocket_out').sendText(json.dumps({
        'type': 'geometry_update',
        'capsule_id': capsule_id,
        'geometry_url': f"http://localhost:8080/{export_path}"
    }))
```

---

## 🎯 **Capsule Status Visualizations**

### **Critical (Red, Pulsing, Spiky)**

**Visual Parameters:**
- Geometry: Icosphere with spikes (vibration-based)
- Color: Temperature gradient (blue → red)
- Animation: Fast pulse (1-5 Hz)
- Audio Reactive: Bass → scale modulation
- Emissive: High (0.8)

**TouchDesigner Network:**
```
osc_in → math_chop → icosphere_sop → spike_sop → transform_sop → geo_comp
                                                                      ↓
audio_in → audio_analyzer → math_chop → constant_mat → render_top → export
```

---

### **Warning (Amber, Rotating, Glowing)**

**Visual Parameters:**
- Geometry: Cube
- Color: Amber (#ffaa33)
- Animation: Rotation (30-120 deg/sec)
- Glow: Pressure-based (0.3-1.0)
- Emissive: Medium (0.5-0.8)

**TouchDesigner Network:**
```
osc_in → math_chop → box_sop → transform_sop → geo_comp
                                                  ↓
                      constant_mat → render_top → export
```

---

### **Active (Green, Flowing, Smooth)**

**Visual Parameters:**
- Geometry: Torus
- Color: Green (#33ff33)
- Animation: Smooth rotation (20-60 deg/sec)
- Flow: Production rate-based
- Emissive: Low (0.3-0.5)

**TouchDesigner Network:**
```
osc_in → math_chop → torus_sop → transform_sop → geo_comp
                                                    ↓
                      constant_mat → render_top → export
```

---

## 🚀 **Integration with Three.js**

### **1. Load Exported Geometry**

```typescript
import * as THREE from 'three';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';

const loader = new OBJLoader();

// Load geometry from TouchDesigner
loader.load('http://localhost:8080/exports/capsule_001.obj', (object) => {
  scene.add(object);
});
```

### **2. Load Exported Texture**

```typescript
const textureLoader = new THREE.TextureLoader();

// Load texture from TouchDesigner
textureLoader.load('http://localhost:8080/exports/capsule_001_diffuse.png', (texture) => {
  material.map = texture;
  material.needsUpdate = true;
});
```

### **3. Real-Time Updates via WebSocket**

```typescript
const ws = new WebSocket('ws://localhost:9980');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'texture_update') {
    // Update texture
    textureLoader.load(data.texture_url, (texture) => {
      material.map = texture;
      material.needsUpdate = true;
    });
  }
  
  if (data.type === 'geometry_update') {
    // Update geometry
    loader.load(data.geometry_url, (object) => {
      scene.remove(oldObject);
      scene.add(object);
    });
  }
};
```

---

## 📈 **Performance Optimization**

### **TouchDesigner Settings**

- **Resolution:** 1920×1080 (Full HD)
- **Frame Rate:** 60 fps
- **Texture Format:** PNG (lossless) or JPG (compressed)
- **Geometry Format:** OBJ (simple) or FBX (complex)

### **Export Optimization**

- **Texture Compression:** Use JPG for real-time updates (smaller file size)
- **Geometry Simplification:** Reduce polygon count for web export
- **Update Rate:** Export every 2-3 frames (20-30 fps) instead of every frame

### **WebSocket Optimization**

- **Binary Protocol:** Use binary WebSocket for geometry/texture data
- **Delta Updates:** Only send changed data
- **Compression:** Use gzip compression for JSON messages

---

## 🎨 **Creative Variations**

### **1. Particle Systems**

```python
# Particle emission based on production rate
production_rate = op('osc_in')['production_rate']
emission_rate = 10 + (production_rate / 100) * 90

op('particle1').par.birthrate = emission_rate
```

### **2. Displacement Noise**

```python
# Noise amplitude based on vibration
vibration = op('osc_in')['vibration']
noise_amplitude = 0.01 + (vibration / 100) * 0.1

op('noise1').par.amp = noise_amplitude
```

### **3. Fractal Geometry**

```python
# Fractal iterations based on complexity
complexity = op('osc_in')['complexity']
iterations = int(1 + (complexity / 100) * 5)  # 1-6 iterations

op('fractal1').par.iterations = iterations
```

---

## 📚 **Resources**

1. **TouchDesigner + Three.js Tutorial:** https://github.com/benjaminben/td-threejs-tutorial
2. **Enhanced Web Workflows:** https://derivative.ca/community-post/tutorial/enhanced-web-workflows-touchdesigner-threejs/63831
3. **TouchDesigner Documentation:** https://docs.derivative.ca
4. **OSC Protocol:** https://opensoundcontrol.stanford.edu

---

## 🚀 **Next Steps**

1. **Create TouchDesigner project file** (.toe)
2. **Set up OSC/WebSocket input**
3. **Build procedural geometry networks**
4. **Configure texture export**
5. **Test real-time updates**
6. **Optimize for web deployment**

---

**Status:** Template ready. Requires TouchDesigner 2023.11760 or later.

**Performance:** 60 fps rendering + 30 fps export = **Smooth generative art!** 🎨
