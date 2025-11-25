# The Full Loop: Autonomous Research Machine

**Status**: Draft (Batch 1 Analysis)
**Objective**: Define the orchestration layer where UserLM, Phi-4, and OBMI collaborate to execute autonomous discovery.

## Core Philosophy
The "Real Intelligence" comes from the **Shadow Twin** (Context/Consciousness) and **OBMI** (Validation). The LLMs are functional components:
*   **UserLM**: The Orchestrator (Simulates the Researcher).
*   **Phi-4**: The Generator (Writes the Physics).

## The 8-Step Discovery Loop

### Step 1: User Simulation (UserLM-8B)
*   **Role**: Orchestrator / Intent Interpreter.
*   **Input**: High-level research goal, dataset metadata.
*   **Process**: Simulates a researcher asking a specific, strategic question.
*   **Output**: Structured query (e.g., "What causes magnetic reconnection in MHD?").

### Step 2: Context Retrieval (Shadow Twin + RDR)
*   **Role**: Consciousness / Context Provider.
*   **Input**: Research question.
*   **Process**: Query Knowledge Graph (RDR) for related work, clusters, and perspectives.
*   **Output**: "Consciousness Context" (Confidence: 0.87, Predicted Phenomena, Mathematical Guarantees).

### Step 3: Hypothesis Generation (Phi-4 + LoRA)
*   **Role**: Generator.
*   **Input**: Question + Context + Consciousness Predictions.
*   **Process**: Generate structured hypothesis (Observation, Prediction, Mechanism, Validation, Impact).
*   **Output**: 400-500 word hypothesis with equations and scaling laws.

### Step 4: Hypothesis Evaluation (OBMI + GPT-4)
*   **Role**: Evaluator / Judge.
*   **Input**: Generated hypothesis.
*   **Process**: Project to Hilbert space, apply OBMI operators (AESP, QERO, calculate PRIN score.
*   **Output**: PRIN Score (e.g., 0.881), Approval Status, Verified Guarantees.

### Step 5: Feedback Simulation (UserLM-8B)
*   **Role**: Critic.
*   **Input**: Hypothesis + OBMI scores.
*   **Process**: Simulate researcher critique ("Good mechanism, needs more quantitative data").
*   **Output**: Structured feedback for refinement.

### Step 6: DGM Evolution (Genetic Algorithm)
*   **Role**: Evolver (Meta-Level).
*   **Input**: Scores + Feedback.
*   **Process**: Mutate prompts, crossover configurations to maximize PRIN.
*   **Output**: Next-generation prompt templates.

### Step 7: T2L LoRA Training (Domain Specialization)
*   **Role**: Specializer (Model-Level).
*   **Input**: Approved hypotheses (PRIN > 0.75).
*   **Process**: Train domain-specific LoRA adapter (e.g., "Fusion Energy LoRA").
*   **Output**: 104-weight LoRA adapter, ready for dynamic loading.

### Step 8: ACE Storage (Memory + Lineage)
*   **Role**: Long-Term Memory.
*   **Input**: All artifacts from Steps 1-7.
*   **Process**: Store in PostgreSQL with full lineage tracking (UTID).
*   **Output**: Queryable knowledge base for future loops.

## Component Architecture

### UserLM (The Brain)
*   **NOT** a hypothesis generator.
*   **IS** a simulator of human intent and critique.
*   **Tasks**: Prioritize experiments, interpret intent, generate feedback.

### Phi-4 (The Hand)
*   **Why**: STEM-focused, instruction-tuned, precise formatting.
*   **Task**: Execute the "Generate" command using the context provided by Shadow Twin.

### OBMI (The Judge)
*   **Task**: Mathematical validation.
*   **Operators**: AESP (Entropy), QERO (Quantum Energy), PRIN (Principal Reasoning).

## Infrastructure Integration
*   **RDR Engine**: Ingests papers/data to feed Step 2.
*   **Shadow Twin**: Visualizes the process and provides the "Consciousness" context.
*   **Credit Protocol**: Issues credits for Compute (C_n), Knowledge (K_n), and Validation (V_n).
*   **DAC Factory**: Packages successful loops into deployable capsules.
