# Industriverse: The Thermodynamic Computing Platform

**"Where Energy Meets Intelligence"**

Industriverse is a next-generation AI platform that governs generative models using thermodynamic principles. By grounding AI in the laws of physics (Energy, Entropy, Exergy), we enable autonomous scientific discovery and industrial optimization that is not just plausible, but physically valid.

## Core Concepts

### 1. Thermodynamic AI
Unlike traditional AI that optimizes for human preference (RLHF), Industriverse optimizes for **Energy Minimization**. We use **Energy-Based Models (EBMs)** and **Thermodynamic Neural Networks (TNNs)** to predict the "energy landscape" of a system, guiding generation towards stable, efficient, and realizable states.

### 2. The Capsule Protocol (`capsule://`)
A sovereign, portable data structure for the knowledge economy. A Capsule encapsulates:
*   **Hypothesis**: The design or idea.
*   **Proof**: The verification data.
*   **Metadata**: Lineage and ownership.

### 3. The Discovery Loop
An autonomous engine that iterates through **Hypothesis -> Design -> Simulation -> Validation**, accelerating the pace of innovation.

## Getting Started

### Prerequisites
*   Python 3.10+
*   Node.js 18+ (for Frontend)

### Installation
```bash
git clone https://github.com/industriverse/industriverse.git
cd industriverse
pip install -r requirements.txt
```

### Running the Frontend (Dyson Sphere)
The "Dyson Sphere" is our immersive 3D interface for visualizing the thermodynamic state of the system.

```bash
cd frontend
npm install
npm run dev
```

### Using the SDK
```python
from src.core.capsule_uri import CapsuleURI
from src.tnn.predictor import TNNPredictor

# Initialize the Client (Public Mode)
predictor = TNNPredictor()

# Create a Capsule
uri = CapsuleURI("fusion_v1", "capsule://industriverse/fusion/reactor_01")
print(f"Created Capsule: {uri}")

# Predict Energy (Mock/API)
energy = predictor.predict_energy(state=[0.5, 0.9])
print(f"System Energy: {energy}")
```

## Enterprise Edition
The core **Thermodynamic Engine** (TNN Training, EBDM Generation, and the full Energy Prior Library) is available in the Enterprise Edition. This repository provides the **Protocol**, the **Frontend**, and the **Client SDK** to interface with the platform.

## License
Proprietary / Business Source License. See `LICENSE` for details.
