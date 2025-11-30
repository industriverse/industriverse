# Aletheia & Dark Factory Architecture: The Quadrality

**Technical Specification for the Truth Layer and Lights-Out Autopilot.**

---

## 1. The Quadrality
We upgrade the Trinity (Chronos-Kairos-Telos) to a **Quadrality** by adding **Aletheia**.

### Aletheia (The Truth Layer)
*   **Role**: The "Supreme Court" of Physics.
*   **Inputs**: `VisualTwin` (Camera), `MFEM` (Embeddings), `Sensors` (Telemetry).
*   **Logic**:
    ```python
    prediction = simulation.get_state()
    reality = aletheia.observe()
    drift = distance(prediction, reality)
    
    if drift > threshold:
        raise PhysicsViolation("Model Hallucination Detected")
    ```

## 2. The Dark Factory Controller (`src/orchestration/dark_factory.py`)
*   **Role**: The Autopilot.
*   **Loop**:
    1.  **Observe**: Poll Aletheia for "Truth Score".
    2.  **Orient**: Consult EMM for "Market Stance".
    3.  **Decide**: Adjust Kairos "Bid Multipliers".
    4.  **Act**: Dispatch tasks via Chronos.

## 3. The Entropy Market Maker (EMM) (`src/orchestration/emm.py`)
*   **Role**: The Economist Agent.
*   **Algorithm**: Reinforcement Learning (PPO/DQN).
*   **State**: Grid Price, Factory Load, Order Backlog.
*   **Action**: Set `global_energy_budget`, `min_negentropy_threshold`.
*   **Reward**: Profit (Value Produced - Energy Cost).

## 4. Factory Personas
*   **Aggressive**: High Risk, High Bid, Low Safety Margin.
*   **Conservative**: Low Risk, Low Bid, High Safety Margin.
*   **Balanced**: Adaptive.

## 5. Data Flow (The Loop)
1.  **Chronos** schedules a task.
2.  **Kairos** approves it based on **EMM** parameters.
3.  **Executor** runs it.
4.  **Aletheia** validates the result against Physics.
5.  **Telos** handles any failures.
6.  **EMM** learns from the profit/loss.
