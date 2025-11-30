# Orchestration System V2: The Trinity Engine

**Technical Specification for the "Nervous System" of Empeiria Haus.**

---

## 1. Core Concept
The system moves beyond "Cron" (Time-based) to "Teleological" (Purpose-based) and "Economic" (Value-based) orchestration.

## 2. The Task Schema (Entropy-Aware)
Every task in the system is an economic entity.

```json
{
  "id": "task_123",
  "name": "fusion_simulation_run",
  "type": "SIMULATION",
  "status": "PENDING",
  "dependencies": ["ingest_data_batch_99"],
  
  // Chronos Fields (Time)
  "schedule": "@daily",
  "timeout_seconds": 3600,
  
  // Kairos Fields (Economics)
  "energy_cost_est_kwh": 5.5,
  "negentropy_value_score": 0.95,  // 0.0 to 1.0 (High Value)
  "max_bid_price": 0.10,           // Max $ per kWh willing to pay
  
  // Telos Fields (Purpose)
  "priority": "CRITICAL",
  "self_healing_policy": "DIAGNOSE_AND_RETRY",
  "owner_persona": "research_lead"
}
```

## 3. Component Architecture

### A. Chronos (The DAG Runner)
*   **Responsibility**: Maintains the dependency graph.
*   **Loop**:
    1.  Polls `TaskDB` for `status=PENDING`.
    2.  Checks `dependencies`. Are they `COMPLETED`?
    3.  If yes, pushes to **Kairos Queue**.

### B. Kairos (The Optimizer)
*   **Responsibility**: Decides *execution time* based on external factors.
*   **Logic**:
    ```python
    current_energy_price = get_grid_price()
    task_value = task.negentropy_value_score * task.market_multiplier
    
    if current_energy_price > task.max_bid_price and task.priority != "CRITICAL":
        return "DEFER"
    else:
        return "EXECUTE"
    ```

### C. Telos (The Supervisor)
*   **Responsibility**: Monitors execution and handles failure.
*   **Logic**:
    *   **Success**: Updates `TaskDB`, triggers downstream Chronos events.
    *   **Failure**:
        1.  Captures `stderr`.
        2.  Invokes `Trifecta` (LLM) to analyze error.
        3.  If fixable (e.g., "Missing Config"), applies fix and re-queues.
        4.  If fatal, alerts Human.

## 4. Data Flow
1.  **Client Intake** -> Creates `Task` (Telos).
2.  **Chronos** -> Sees new Task, checks dependencies.
3.  **Kairos** -> Evaluates cost/benefit. Approves execution.
4.  **Executor** -> Runs the code.
5.  **Telos** -> Verifies output (Negentropy Audit).

## 5. Technology Stack
*   **Language**: Python 3.9+
*   **DB**: SQLite (MVP) -> PostgreSQL (Prod).
*   **Async**: `asyncio` for non-blocking orchestration.
*   **LLM Integration**: `Trifecta` API for Telos diagnosis.
