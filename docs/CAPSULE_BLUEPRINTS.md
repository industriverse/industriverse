# The 27 Capsule "Thermodynamic Blueprints"

This document serves as the canonical reference for the 27 Sovereign Capsules deployed in the Industriverse Thermodynamic Discovery Loop V16.

## Category A: High-Energy & Dynamic Systems
*Physics Topology: Magnetohydrodynamics (MHD), Plasma Physics, High-Entropy Alloys*

### 1. Fusion Reactor Control (capsule:fusion:v1)
*   **Physics Topology:** MHD Stability, Plasma Confinement
*   **Domain Equations:** Grad-Shafranov, MHD Ideal Stability
*   **Energy Prior:** `MHD_64_energy_map.npz`
*   **PRIN Config:** α=0.6, β=0.3, γ=0.1 (Threshold: 0.85)
*   **Safety Budget:** Soft: 5000J, Hard: 20000J

### 2. Electric Motor Manufacturing (capsule:motor:v1)
*   **Physics Topology:** Electromagnetic Fields, Torque Ripple
*   **Domain Equations:** Maxwell's Equations, Lorentz Force
*   **Energy Prior:** `MHD_64_energy_map.npz`
*   **PRIN Config:** α=0.6, β=0.3, γ=0.1
*   **Safety Budget:** Soft: 1000J, Hard: 5000J

### 3. Magnet Assemblies (capsule:magnet:v1)
*   **Physics Topology:** Ferromagnetism, Hysteresis
*   **Domain Equations:** Landau-Lifshitz-Gilbert
*   **Energy Prior:** `MHD_64_energy_map.npz`
*   **PRIN Config:** α=0.65, β=0.25, γ=0.1
*   **Safety Budget:** Soft: 1000J, Hard: 5000J

### 4. Battery Electrode Formation (capsule:battery:v1)
*   **Physics Topology:** Ion Transport, Electrochemical Kinetics
*   **Domain Equations:** Butler-Volmer, Nernst-Planck
*   **Energy Prior:** `chemistry_reaction_map` (Alias: `turbulent_radiative_layer_2D_energy_map`)
*   **PRIN Config:** α=0.66, β=0.24, γ=0.1
*   **Safety Budget:** Soft: 3500J, Hard: 15000J

### 5. CNC Torque Machining (capsule:cnc:v1)
*   **Physics Topology:** Rotational Dynamics, Shear Stress
*   **Domain Equations:** Cutting Force Model, Euler-Bernoulli Beam
*   **Energy Prior:** `MHD_64_energy_map.npz`
*   **PRIN Config:** α=0.5, β=0.35, γ=0.15
*   **Safety Budget:** Soft: 50J, Hard: 250J

### 6. EV Chassis Alignment (capsule:chassis:v1)
*   **Physics Topology:** Kinematics, Structural Mechanics
*   **Domain Equations:** Rigid Body Dynamics, Stress-Strain
*   **Energy Prior:** `MHD_64_energy_map.npz`
*   **PRIN Config:** α=0.5, β=0.4, γ=0.1
*   **Safety Budget:** Soft: 100J, Hard: 500J

### 7. Microgrid Pulse Stability (capsule:microgrid:v1)
*   **Physics Topology:** Power Flow, Transient Stability
*   **Domain Equations:** Swing Equation, Kirchhoff's Laws
*   **Energy Prior:** `MHD_64_energy_map.npz`
*   **PRIN Config:** α=0.55, β=0.35, γ=0.1
*   **Safety Budget:** Soft: 2000J, Hard: 8000J

---

## Category B: Flow, Heat & Pressure
*Physics Topology: Fluid Dynamics, Thermodynamics, Chemical Kinetics*

### 8. Casting & Foundry (capsule:casting:v1)
*   **Physics Topology:** Multiphase Flow, Solidification
*   **Domain Equations:** Navier-Stokes, Stefan Condition
*   **Energy Prior:** `turbulent_radiative_layer_2D_energy_map.npz`
*   **PRIN Config:** α=0.58, β=0.3, γ=0.12
*   **Safety Budget:** Soft: 800J, Hard: 3500J

### 9. Heat Treatment (capsule:heat:v1)
*   **Physics Topology:** Thermal Diffusion, Phase Transformation
*   **Domain Equations:** Heat Equation, Arrhenius Equation
*   **Energy Prior:** `turbulent_radiative_layer_2D_energy_map.npz`
*   **PRIN Config:** α=0.6, β=0.25, γ=0.15
*   **Safety Budget:** Soft: 2000J, Hard: 10000J

### 10. Chemical Reactors (capsule:chem:v1)
*   **Physics Topology:** Reaction Kinetics, Mass Transfer
*   **Domain Equations:** Reaction Rate Laws, Mass Balance
*   **Energy Prior:** `chemistry_reaction_map` (Alias: `turbulent_radiative_layer_2D_energy_map`)
*   **PRIN Config:** α=0.63, β=0.27, γ=0.1
*   **Safety Budget:** Soft: 3000J, Hard: 12000J

### 11. Polymer Molding (capsule:polymer:v1)
*   **Physics Topology:** Non-Newtonian Flow, Viscoelasticity
*   **Domain Equations:** Cross-WLF Viscosity, Giesekus Model
*   **Energy Prior:** `turbulent_radiative_layer_2D_energy_map.npz`
*   **PRIN Config:** α=0.58, β=0.3, γ=0.12
*   **Safety Budget:** Soft: 600J, Hard: 2500J

### 12. Metallurgical Thermal Cycles (capsule:metal:v1)
*   **Physics Topology:** Grain Growth, Recrystallization
*   **Domain Equations:** Hall-Petch, JMAK Equation
*   **Energy Prior:** `turbulent_radiative_layer_2D_energy_map.npz`
*   **PRIN Config:** α=0.6, β=0.25, γ=0.15
*   **Safety Budget:** Soft: 2000J, Hard: 10000J

### 13. Pipeline Fluid Control (capsule:pipeline:v1)
*   **Physics Topology:** Pipe Flow, Turbulence
*   **Domain Equations:** Darcy-Weisbach, Colebrook Equation
*   **Energy Prior:** `turbulent_radiative_layer_2D_energy_map.npz`
*   **PRIN Config:** α=0.52, β=0.38, γ=0.1
*   **Safety Budget:** Soft: 150J, Hard: 600J

### 14. Quality Control Thermal (capsule:qctherm:v1)
*   **Physics Topology:** IR Thermography, Heat Signatures
*   **Domain Equations:** Planck's Law, Stefan-Boltzmann
*   **Energy Prior:** `turbulent_radiative_layer_2D_energy_map.npz`
*   **PRIN Config:** α=0.6, β=0.3, γ=0.1
*   **Safety Budget:** Soft: 120J, Hard: 500J

### 15. Failure Analysis (capsule:failure:v1)
*   **Physics Topology:** Fracture Mechanics, Fatigue
*   **Domain Equations:** Paris Law, Griffith Criterion
*   **Energy Prior:** `turbulent_radiative_layer_2D_energy_map.npz`
*   **PRIN Config:** α=0.6, β=0.3, γ=0.1
*   **Safety Budget:** Soft: 120J, Hard: 500J

---

## Category C: Swarm, Logistics & Active Matter
*Physics Topology: Active Matter, Agent-Based Modeling, Network Theory*

### 16. Warehouse Robotics (capsule:robotics:v1)
*   **Physics Topology:** Swarm Dynamics, Collision Avoidance
*   **Domain Equations:** Vicsek Model, Social Force Model
*   **Energy Prior:** `active_matter_energy_map.npz`
*   **PRIN Config:** α=0.48, β=0.42, γ=0.1
*   **Safety Budget:** Soft: 80J, Hard: 400J

### 17. Material Flow (capsule:matflow:v1)
*   **Physics Topology:** Flow Networks, Queueing Theory
*   **Domain Equations:** Little's Law, Max-Flow Min-Cut
*   **Energy Prior:** `active_matter_energy_map.npz`
*   **PRIN Config:** α=0.4, β=0.45, γ=0.15
*   **Safety Budget:** Soft: 30J, Hard: 150J

### 18. Workforce Routing (capsule:workforce:v1)
*   **Physics Topology:** Traveling Salesman, Optimization
*   **Domain Equations:** Bellman Equation, VRP Algorithms
*   **Energy Prior:** `active_matter_energy_map.npz`
*   **PRIN Config:** α=0.4, β=0.45, γ=0.15
*   **Safety Budget:** Soft: 30J, Hard: 150J

### 19. Scheduling (capsule:schedule:v1)
*   **Physics Topology:** Temporal Logic, Constraint Satisfaction
*   **Domain Equations:** Job Shop Scheduling, Gantt Logic
*   **Energy Prior:** `active_matter_energy_map.npz`
*   **PRIN Config:** α=0.4, β=0.45, γ=0.15
*   **Safety Budget:** Soft: 20J, Hard: 100J

### 20. AMR Safety Sensing (capsule:amrsafety:v1)
*   **Physics Topology:** Lidar/Vision Fields, Obstacle Detection
*   **Domain Equations:** Kalman Filter, SLAM
*   **Energy Prior:** `active_matter_energy_map.npz`
*   **PRIN Config:** α=0.48, β=0.42, γ=0.1
*   **Safety Budget:** Soft: 80J, Hard: 400J

### 21. Conveyor Coordination (capsule:conveyor:v1)
*   **Physics Topology:** Coupled Oscillators, Synchronization
*   **Domain Equations:** Kuramoto Model
*   **Energy Prior:** `active_matter_energy_map.npz`
*   **PRIN Config:** α=0.48, β=0.42, γ=0.1
*   **Safety Budget:** Soft: 80J, Hard: 400J

### 22. Assembly Line Balancing (capsule:assembly:v1)
*   **Physics Topology:** Line Balancing, Takt Time
*   **Domain Equations:** Salveson's Algorithm
*   **Energy Prior:** `active_matter_energy_map.npz`
*   **PRIN Config:** α=0.5, β=0.4, γ=0.1
*   **Safety Budget:** Soft: 80J, Hard: 400J

---

## Category D: Multi-Physics & Complexity
*Physics Topology: Coupled Systems, Entropy Gradients, Supernova Dynamics*

### 23. Electronics Assembly (capsule:electronics:v1)
*   **Physics Topology:** Thermal-Mechanical-Electrical Coupling
*   **Domain Equations:** Coupled PDEs
*   **Energy Prior:** `supernova_explosion_64_energy_map.npz`
*   **PRIN Config:** α=0.5, β=0.4, γ=0.1
*   **Safety Budget:** Soft: 120J, Hard: 600J

### 24. PCB Manufacturing (capsule:pcbmfg:v1)
*   **Physics Topology:** Etching, Plating, Lamination
*   **Domain Equations:** Diffusion-Limited Aggregation
*   **Energy Prior:** `supernova_explosion_64_energy_map.npz`
*   **PRIN Config:** α=0.5, β=0.4, γ=0.1
*   **Safety Budget:** Soft: 120J, Hard: 600J

### 25. Sensor Integration (capsule:sensorint:v1)
*   **Physics Topology:** Signal Processing, Noise Dynamics
*   **Domain Equations:** Shannon Entropy, Fourier Transform
*   **Energy Prior:** `supernova_explosion_64_energy_map.npz`
*   **PRIN Config:** α=0.5, β=0.35, γ=0.15
*   **Safety Budget:** Soft: 40J, Hard: 200J

### 26. Surface Finishing (capsule:surface:v1)
*   **Physics Topology:** Surface Tension, Wetting
*   **Domain Equations:** Young-Laplace
*   **Energy Prior:** `supernova_explosion_64_energy_map.npz`
*   **PRIN Config:** α=0.56, β=0.3, γ=0.14
*   **Safety Budget:** Soft: 100J, Hard: 400J

### 27. Lifecycle Analytics (capsule:lifecycle:v1)
*   **Physics Topology:** Reliability Engineering, Decay Models
*   **Domain Equations:** Weibull Distribution, Bathtub Curve
*   **Energy Prior:** `supernova_explosion_64_energy_map.npz`
*   **PRIN Config:** α=0.6, β=0.3, γ=0.1
*   **Safety Budget:** Soft: 120J, Hard: 500J
