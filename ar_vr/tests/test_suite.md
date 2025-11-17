# Week 15 AR/VR Integration - Comprehensive Test Suite

**Test Coverage:** Unit, Integration, Performance, Cross-Platform, Factory Environment, End-to-End

**Test Date:** November 17, 2025  
**Tester:** Automated + Manual  
**Target:** 100% Pass Rate

---

## 📋 **Test Categories**

1. **Unit Tests** - Individual component functionality
2. **Integration Tests** - Component interaction
3. **Performance Tests** - FPS, latency, memory
4. **Cross-Platform Tests** - Mobile AR, VR, desktop
5. **Factory Environment Tests** - Real-world conditions
6. **End-to-End Tests** - Complete user workflows

---

## 🧪 **1. Unit Tests**

### **1.1 MediaPipe Hands Controller**

#### **Test: Hand Detection**
```typescript
describe('MediaPipeHandsController', () => {
  test('should detect hand landmarks', async () => {
    const controller = new MediaPipeHandsController({
      videoElement: mockVideo,
      scene: mockScene,
      camera: mockCamera
    });
    
    await controller.start();
    
    // Simulate hand detection
    const handData = controller.getHandData();
    
    expect(handData).not.toBeNull();
    expect(handData.landmarks).toHaveLength(21);
    expect(handData.handedness).toMatch(/Left|Right/);
  });
});
```

**Expected Result:** ✅ Hand detected with 21 landmarks

---

#### **Test: Pinch Gesture Recognition**
```typescript
test('should recognize pinch gesture', () => {
  const landmarks = createMockLandmarks({
    thumbTip: new THREE.Vector3(0, 0, 0),
    indexTip: new THREE.Vector3(0.2, 0, 0)  // Distance: 0.2
  });
  
  const gesture = controller.recognizeGesture(landmarks, 'Right');
  
  expect(gesture.type).toBe('pinch');
  expect(gesture.confidence).toBeGreaterThan(0.7);
});
```

**Expected Result:** ✅ Pinch gesture recognized with confidence > 0.7

---

#### **Test: 2D to 3D Depth Conversion**
```typescript
test('should convert 2D hand position to 3D depth', () => {
  const landmarks = createMockLandmarks({
    wrist: new THREE.Vector3(0, 0, 0),
    middleFingerPIP: new THREE.Vector3(0.5, 0.5, 0)
  });
  
  const depth = controller.calculateDepth(landmarks);
  
  expect(depth).toBeGreaterThanOrEqual(-2);
  expect(depth).toBeLessThanOrEqual(4);
});
```

**Expected Result:** ✅ Depth within range (-2 to 4)

---

### **1.2 MediaPipe Pose Controller**

#### **Test: Pose Detection**
```typescript
describe('MediaPipePoseController', () => {
  test('should detect pose landmarks', async () => {
    const controller = new MediaPipePoseController({
      videoElement: mockVideo
    });
    
    await controller.start();
    
    const poseData = controller.getPoseData();
    
    expect(poseData).not.toBeNull();
    expect(poseData.landmarks).toHaveLength(33);
    expect(poseData.posture).toMatch(/standing|sitting|bending|reaching|crouching/);
  });
});
```

**Expected Result:** ✅ Pose detected with 33 landmarks

---

#### **Test: Thumbs Up Recognition**
```typescript
test('should recognize thumbs up gesture', () => {
  const landmarks = createMockPoseLandmarks({
    rightThumb: new THREE.Vector3(0, 0.8, 0),  // Above shoulder
    rightWrist: new THREE.Vector3(0, 0.5, 0),
    rightShoulder: new THREE.Vector3(0, 0.6, 0)
  });
  
  const command = controller.recognizeBodyLanguage(landmarks);
  
  expect(command.type).toBe('thumbs_up');
  expect(command.side).toBe('right');
});
```

**Expected Result:** ✅ Thumbs up recognized

---

#### **Test: REBA Score Calculation**
```typescript
test('should calculate REBA score correctly', () => {
  const landmarks = createMockPoseLandmarks({
    // Bending posture (high risk)
    nose: new THREE.Vector3(0, 0.3, 0),
    hip: new THREE.Vector3(0, 0.5, 0)
  });
  
  const risk = controller.calculateErgonomicRisk(landmarks);
  
  expect(risk.rebaScore).toBeGreaterThan(7);  // High risk
  expect(risk.riskLevel).toMatch(/high|very_high/);
});
```

**Expected Result:** ✅ REBA score > 7 for bending posture

---

### **1.3 TouchDesigner Data Visualizer**

#### **Test: Geometry Generation**
```typescript
describe('TouchDesignerDataVisualizer', () => {
  test('should generate critical capsule geometry', () => {
    const visualizer = new TouchDesignerDataVisualizer({
      scene: mockScene
    });
    
    const mesh = visualizer.createVisualization(
      'capsule_001',
      'critical',
      { temperature: 85, vibration: 70, pressure: 60, productionRate: 75, noise: 50, timestamp: Date.now() },
      new THREE.Vector3(0, 1.5, 0)
    );
    
    expect(mesh.geometry).toBeInstanceOf(THREE.BufferGeometry);
    expect(mesh.material).toBeInstanceOf(THREE.MeshStandardMaterial);
    expect(mesh.position).toEqual(new THREE.Vector3(0, 1.5, 0));
  });
});
```

**Expected Result:** ✅ Geometry generated correctly

---

#### **Test: Temperature-Based Color**
```typescript
test('should map temperature to color gradient', () => {
  const material = visualizer.generateMaterial('critical', {
    temperature: 85,  // High temperature
    pressure: 60,
    vibration: 70,
    productionRate: 75,
    noise: 50,
    timestamp: Date.now()
  });
  
  const color = material.color;
  
  // High temperature should be red (hue close to 0)
  const hsl = { h: 0, s: 0, l: 0 };
  color.getHSL(hsl);
  
  expect(hsl.h).toBeLessThan(0.2);  // Red range
});
```

**Expected Result:** ✅ High temperature → Red color

---

#### **Test: Audio Reactive Modulation**
```typescript
test('should apply audio reactive modulation', () => {
  const audioData = new Uint8Array(256);
  audioData.fill(200);  // High audio level
  
  const mesh = mockMesh;
  visualizer.applyAudioReactive(mesh, audioData);
  
  // Scale should increase with audio level
  expect(mesh.scale.x).toBeGreaterThan(1);
  
  // Emissive intensity should increase
  if (mesh.material instanceof THREE.MeshStandardMaterial) {
    expect(mesh.material.emissiveIntensity).toBeGreaterThan(0.5);
  }
});
```

**Expected Result:** ✅ Audio modulation applied correctly

---

## 🔗 **2. Integration Tests**

### **2.1 MediaPipe + Three.js Integration**

#### **Test: Hand Cursor Position in 3D Scene**
```typescript
describe('MediaPipe + Three.js Integration', () => {
  test('should update 3D cursor based on hand position', async () => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
    
    const controller = new MediaPipeHandsController({
      videoElement: mockVideo,
      scene,
      camera
    });
    
    await controller.start();
    
    // Simulate hand movement
    simulateHandMovement({ x: 0.5, y: 0.5, z: 0 });
    
    const handData = controller.getHandData();
    const cursor = scene.getObjectByName('hand_cursor');
    
    expect(cursor).not.toBeUndefined();
    expect(cursor.position).toEqual(handData.cursorPosition);
  });
});
```

**Expected Result:** ✅ Cursor follows hand position

---

### **2.2 MediaPipe + Capsule Selection**

#### **Test: Pinch Gesture Selects Capsule**
```typescript
test('should select capsule on pinch gesture', async () => {
  const scene = new THREE.Scene();
  
  // Add capsule
  const capsule = new THREE.Mesh(
    new THREE.SphereGeometry(0.15),
    new THREE.MeshStandardMaterial()
  );
  capsule.position.set(0, 1.5, 0);
  capsule.userData.type = 'capsule_overlay';
  scene.add(capsule);
  
  const controller = new MediaPipeHandsController({
    videoElement: mockVideo,
    scene,
    camera: mockCamera,
    onCapsuleSelect: jest.fn()
  });
  
  // Simulate hand over capsule + pinch
  simulateHandPosition({ x: 0, y: 1.5, z: 0 });
  simulatePinchGesture();
  
  expect(controller.config.onCapsuleSelect).toHaveBeenCalledWith(capsule);
});
```

**Expected Result:** ✅ Capsule selected on pinch

---

### **2.3 TouchDesigner + WebSocket Integration**

#### **Test: Real-Time Metrics Update**
```typescript
test('should update visualization on WebSocket message', async () => {
  const visualizer = new TouchDesignerDataVisualizer({
    scene: mockScene,
    websocketUrl: 'ws://localhost:9980'
  });
  
  // Create capsule
  visualizer.createVisualization(
    'capsule_001',
    'critical',
    { temperature: 50, pressure: 60, vibration: 30, productionRate: 75, noise: 50, timestamp: Date.now() },
    new THREE.Vector3(0, 1.5, 0)
  );
  
  // Simulate WebSocket message
  mockWebSocket.send(JSON.stringify({
    type: 'metrics_update',
    capsule_id: 'capsule_001',
    metrics: { temperature: 90, pressure: 60, vibration: 30, productionRate: 75, noise: 50, timestamp: Date.now() }
  }));
  
  await waitForUpdate();
  
  const visualization = visualizer.visualizations.get('capsule_001');
  expect(visualization.metrics.temperature).toBe(90);
});
```

**Expected Result:** ✅ Visualization updated via WebSocket

---

## ⚡ **3. Performance Tests**

### **3.1 FPS Benchmarks**

#### **Test: MediaPipe Hands FPS**
```typescript
describe('Performance Tests', () => {
  test('should maintain 30 fps hand tracking', async () => {
    const controller = new MediaPipeHandsController({
      videoElement: mockVideo,
      scene: mockScene,
      camera: mockCamera
    });
    
    await controller.start();
    
    // Run for 5 seconds
    await sleep(5000);
    
    const fps = controller.getFPS();
    
    expect(fps).toBeGreaterThanOrEqual(28);  // Allow 2 fps tolerance
  });
});
```

**Expected Result:** ✅ FPS ≥ 28

---

#### **Test: Three.js Rendering FPS**
```typescript
test('should maintain 60 fps rendering', async () => {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer();
  
  // Add 10 capsules
  for (let i = 0; i < 10; i++) {
    const capsule = new THREE.Mesh(
      new THREE.SphereGeometry(0.15),
      new THREE.MeshStandardMaterial()
    );
    scene.add(capsule);
  }
  
  let frameCount = 0;
  const startTime = performance.now();
  
  function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
    frameCount++;
  }
  
  animate();
  await sleep(5000);
  
  const elapsed = (performance.now() - startTime) / 1000;
  const fps = frameCount / elapsed;
  
  expect(fps).toBeGreaterThanOrEqual(58);  // Allow 2 fps tolerance
});
```

**Expected Result:** ✅ FPS ≥ 58

---

### **3.2 Latency Benchmarks**

#### **Test: Gesture Recognition Latency**
```typescript
test('should recognize gesture within 100ms', async () => {
  const controller = new MediaPipeHandsController({
    videoElement: mockVideo,
    scene: mockScene,
    camera: mockCamera
  });
  
  const startTime = performance.now();
  
  // Simulate pinch gesture
  simulatePinchGesture();
  
  await waitForGestureRecognition();
  
  const latency = performance.now() - startTime;
  
  expect(latency).toBeLessThan(100);
});
```

**Expected Result:** ✅ Latency < 100ms

---

#### **Test: WebSocket Update Latency**
```typescript
test('should receive WebSocket update within 50ms', async () => {
  const visualizer = new TouchDesignerDataVisualizer({
    scene: mockScene,
    websocketUrl: 'ws://localhost:9980'
  });
  
  const startTime = performance.now();
  
  // Send metrics update
  mockWebSocket.send(JSON.stringify({
    type: 'metrics_update',
    capsule_id: 'capsule_001',
    metrics: { temperature: 85, pressure: 60, vibration: 70, productionRate: 75, noise: 50, timestamp: Date.now() }
  }));
  
  await waitForUpdate();
  
  const latency = performance.now() - startTime;
  
  expect(latency).toBeLessThan(50);
});
```

**Expected Result:** ✅ Latency < 50ms

---

### **3.3 Memory Usage**

#### **Test: Memory Leak Detection**
```typescript
test('should not leak memory after 1000 updates', async () => {
  const visualizer = new TouchDesignerDataVisualizer({
    scene: mockScene
  });
  
  const initialMemory = performance.memory.usedJSHeapSize;
  
  // Create and remove 1000 visualizations
  for (let i = 0; i < 1000; i++) {
    const capsuleId = `capsule_${i}`;
    
    visualizer.createVisualization(
      capsuleId,
      'critical',
      { temperature: 85, pressure: 60, vibration: 70, productionRate: 75, noise: 50, timestamp: Date.now() },
      new THREE.Vector3(0, 1.5, 0)
    );
    
    visualizer.removeVisualization(capsuleId);
  }
  
  // Force garbage collection
  if (global.gc) global.gc();
  
  const finalMemory = performance.memory.usedJSHeapSize;
  const memoryIncrease = finalMemory - initialMemory;
  
  // Allow 10MB increase
  expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024);
});
```

**Expected Result:** ✅ Memory increase < 10MB

---

## 📱 **4. Cross-Platform Tests**

### **4.1 Mobile AR (iOS/Android)**

#### **Test: Hand Tracking on Mobile**
```
Platform: iPhone 14 Pro (iOS 17)
Browser: Safari
Resolution: 1179×2556

Steps:
1. Open example_mediapipe.html
2. Grant camera permission
3. Enable hand tracking
4. Move hand in front of camera

Expected Result:
✅ Hand detected with 21 landmarks
✅ FPS ≥ 25
✅ Gesture recognition works
✅ Cursor follows hand
```

---

#### **Test: Pose Tracking on Mobile**
```
Platform: Samsung Galaxy S23 (Android 14)
Browser: Chrome
Resolution: 1080×2340

Steps:
1. Open example_mediapipe.html
2. Grant camera permission
3. Enable pose tracking
4. Perform thumbs up gesture

Expected Result:
✅ Pose detected with 33 landmarks
✅ FPS ≥ 25
✅ Thumbs up recognized
✅ REBA score calculated
```

---

### **4.2 VR Headsets**

#### **Test: Meta Quest 3**
```
Platform: Meta Quest 3
Browser: Meta Browser (Chromium)
Resolution: 2064×2208 per eye

Steps:
1. Open example_interaction.html in VR mode
2. Enable VR session
3. Point controller at capsule
4. Pull trigger

Expected Result:
✅ VR session starts
✅ Capsule highlighted on point
✅ Capsule selected on trigger
✅ FPS ≥ 72 (native refresh rate)
```

---

#### **Test: Apple Vision Pro**
```
Platform: Apple Vision Pro
Browser: Safari (visionOS)
Resolution: 3680×3140 per eye

Steps:
1. Open example_interaction.html
2. Enable immersive mode
3. Use gaze + pinch to select capsule

Expected Result:
✅ Immersive mode starts
✅ Gaze tracking works
✅ Pinch gesture selects capsule
✅ FPS ≥ 90 (native refresh rate)
```

---

### **4.3 Desktop**

#### **Test: Windows (Chrome)**
```
Platform: Windows 11
Browser: Chrome 120
GPU: NVIDIA RTX 4090

Steps:
1. Open example_integrated.html
2. Enable webcam
3. Enable hand tracking
4. Enable pose tracking
5. Enable TouchDesigner visualizer

Expected Result:
✅ All features work
✅ Hand tracking FPS ≥ 30
✅ Pose tracking FPS ≥ 30
✅ Rendering FPS ≥ 60
✅ Audio reactive works
```

---

## 🏭 **5. Factory Environment Tests**

### **5.1 Lighting Conditions**

#### **Test: Low Light**
```
Environment: Factory floor (50 lux)
Camera: Logitech C920 (1080p)

Steps:
1. Test hand tracking in low light
2. Measure detection accuracy

Expected Result:
✅ Hand detected (may require increased exposure)
✅ Accuracy ≥ 80%
```

---

#### **Test: Bright Light / Shadows**
```
Environment: Factory floor with overhead lights (500 lux)
Camera: Logitech C920 (1080p)

Steps:
1. Test hand tracking with shadows
2. Measure detection accuracy

Expected Result:
✅ Hand detected despite shadows
✅ Accuracy ≥ 85%
```

---

### **5.2 Glove Compatibility**

#### **Test: Latex Gloves**
```
Glove Type: Latex (thin)
Color: Blue

Steps:
1. Wear latex gloves
2. Test hand tracking
3. Test gesture recognition

Expected Result:
✅ Hand detected
✅ Gestures recognized
✅ Accuracy ≥ 90%
```

---

#### **Test: Work Gloves**
```
Glove Type: Leather work gloves (thick)
Color: Brown

Steps:
1. Wear work gloves
2. Test hand tracking
3. Test gesture recognition

Expected Result:
✅ Hand detected (shape-based)
⚠️ Accuracy may drop to 70-80%
💡 Fallback to pose tracking recommended
```

---

### **5.3 Noise Conditions**

#### **Test: Factory Noise (Audio Reactive)**
```
Environment: Factory floor (85 dB)
Noise Source: Machinery, motors, conveyor belts

Steps:
1. Enable audio reactive visualization
2. Measure frequency response

Expected Result:
✅ Audio captured
✅ Frequency analysis works
✅ Visuals respond to noise
✅ Bass/mid/treble separation works
```

---

## 🎯 **6. End-to-End Tests**

### **6.1 Complete User Workflow**

#### **Test: Gesture-Free Capsule Acknowledgment**
```
Scenario: Factory worker acknowledges critical capsule without touching anything

Steps:
1. Worker sees critical capsule (red, pulsing)
2. Worker points at capsule → capsule highlights
3. Worker pinches fingers → capsule selected
4. Worker gives thumbs up → capsule acknowledged
5. Capsule changes to resolved (gray, fading)

Expected Result:
✅ All steps work seamlessly
✅ No controllers needed
✅ No touch required
✅ Total time < 5 seconds
```

---

#### **Test: Living Data Visualization**
```
Scenario: Factory metrics change, visualizations update in real-time

Steps:
1. Motor temperature increases from 50°C to 85°C
2. Capsule color changes from green to red
3. Vibration increases from 30 Hz to 70 Hz
4. Capsule spikes grow larger
5. Factory noise increases
6. Capsule pulses faster (audio reactive)

Expected Result:
✅ All metrics update in real-time
✅ Visualizations reflect changes
✅ Audio reactive works
✅ Update latency < 100ms
```

---

## 📊 **Test Results Summary**

### **Expected Pass Rate: 100%**

| Category | Tests | Expected Pass | Expected Fail |
|----------|-------|---------------|---------------|
| **Unit Tests** | 12 | 12 | 0 |
| **Integration Tests** | 3 | 3 | 0 |
| **Performance Tests** | 5 | 5 | 0 |
| **Cross-Platform Tests** | 6 | 6 | 0 |
| **Factory Environment Tests** | 6 | 5 | 1* |
| **End-to-End Tests** | 2 | 2 | 0 |
| **TOTAL** | **34** | **33** | **1** |

**Pass Rate:** 97% (33/34)

*Note: Thick work gloves may reduce accuracy to 70-80%, but pose tracking fallback ensures functionality.*

---

## ✅ **Acceptance Criteria**

All tests must pass the following criteria:

### **Functional Requirements**
- ✅ Hand tracking detects 21 landmarks
- ✅ Pose tracking detects 33 landmarks
- ✅ Gesture recognition accuracy ≥ 85%
- ✅ Capsule selection works
- ✅ TouchDesigner visualizations generate correctly
- ✅ WebSocket updates work

### **Performance Requirements**
- ✅ Hand tracking FPS ≥ 28
- ✅ Pose tracking FPS ≥ 28
- ✅ Rendering FPS ≥ 58
- ✅ Gesture latency < 100ms
- ✅ WebSocket latency < 50ms
- ✅ Memory increase < 10MB per 1000 updates

### **Cross-Platform Requirements**
- ✅ Works on iOS Safari
- ✅ Works on Android Chrome
- ✅ Works on Meta Quest 3
- ✅ Works on Apple Vision Pro
- ✅ Works on desktop browsers

### **Factory Environment Requirements**
- ✅ Works in low light (≥ 80% accuracy)
- ✅ Works with shadows (≥ 85% accuracy)
- ✅ Works with latex gloves (≥ 90% accuracy)
- ⚠️ Works with work gloves (≥ 70% accuracy, pose fallback)
- ✅ Audio reactive works with factory noise

---

## 🚀 **Test Execution Plan**

### **Phase 1: Automated Tests (1 hour)**
```bash
npm run test:unit
npm run test:integration
npm run test:performance
```

### **Phase 2: Manual Tests (2 hours)**
- Mobile AR testing (iOS + Android)
- VR headset testing (Quest 3 + Vision Pro)
- Desktop browser testing (Chrome + Edge + Safari)

### **Phase 3: Factory Environment Tests (2 hours)**
- Lighting conditions
- Glove compatibility
- Noise conditions

### **Phase 4: End-to-End Tests (1 hour)**
- Complete user workflows
- Real-time data visualization

**Total Test Time:** 6 hours

---

## 📝 **Test Report Template**

```markdown
# Week 15 AR/VR Integration - Test Report

**Date:** November 17, 2025
**Tester:** [Name]
**Environment:** [Platform/Browser/Device]

## Test Results

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| UT-01 | Hand Detection | ✅ PASS | 21 landmarks detected |
| UT-02 | Pinch Gesture | ✅ PASS | Confidence: 0.85 |
| ... | ... | ... | ... |

## Performance Metrics

- Hand Tracking FPS: 30.2
- Pose Tracking FPS: 29.8
- Rendering FPS: 60.1
- Gesture Latency: 45ms
- WebSocket Latency: 28ms

## Issues Found

None

## Recommendations

All tests passed. Ready for production deployment.

**Overall Status:** ✅ PASS
```

---

**Status:** Test suite ready. Executing tests now...
