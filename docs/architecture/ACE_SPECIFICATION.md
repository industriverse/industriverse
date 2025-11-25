# Agentic Context Engineering (ACE) Specification

**Version:** 1.0
**Status:** Draft
**Layer:** Overseer / Core AI

## 1. Executive Summary

Agentic Context Engineering (ACE) is the meta-framework for continuous self-improvement within the Industriverse. It transforms the system from a static set of models into a learning organism by treating **Context** (prompts, memory, execution traces) as a living, evolving asset. ACE sits between the runtime execution (UserLM/RND1) and the long-term memory, closing the loop between "doing" and "learning."

## 2. Core Philosophy

*   **Context is Code:** The instructions, few-shot examples, and strategies fed to agents are as critical as the model weights.
*   **Append-Only Evolution:** We do not overwrite history; we append "deltas" (improvements) to a growing playbook.
*   **Reflection is Key:** Raw logs are useless without a "Reflection Engine" that extracts meaning (success/failure patterns).
*   **Agentic Diversity:** ACE manages the diversity of agent pools (TUMIX) to ensure robust reasoning.

## 3. System Architecture

ACE operates as a distinct service layer that interacts with all other components.

```mermaid
graph TD
    subgraph Runtime
        UserLM[UserLM (The Operator)]
        RND1[RND1 (The Builder)]
        DAC[DAC Mesh]
    end

    subgraph ACE_Core
        Logger[ACE Memory Logger]
        Reflect[Reflection Engine]
        Playbook[Playbook Manager]
    end

    subgraph Storage
        Logs[(Trajectory Logs)]
        ContextDB[(Context Playbooks)]
    end

    UserLM -->|Emits Logs| Logger
    RND1 -->|Emits Logs| Logger
    DAC -->|Emits Logs| Logger

    Logger -->|Writes| Logs
    Reflect -->|Reads| Logs
    Reflect -->|Extracts Deltas| Playbook
    Playbook -->|Updates| ContextDB
    ContextDB -->|Injects Context| UserLM
    ContextDB -->|Injects Context| RND1
```

## 4. Core Components

### 4.1. ACE Memory Logger (The Scribe)
Captures full execution trajectories from all agents.

*   **Input:** Stream of events (NATS JetStream).
*   **Schema:**
    ```json
    {
      "trace_id": "uuid",
      "agent_id": "userlm-8b-001",
      "timestamp": "iso8601",
      "step_type": "reasoning | tool_use | output",
      "content": "...",
      "context_hash": "sha256_of_input_prompt",
      "outcome": "success | failure | partial",
      "metrics": {
        "latency_ms": 120,
        "tokens": 450,
        "confidence": 0.92
      }
    }
    ```
*   **Storage:** Time-series DB + Vector Store (for semantic retrieval).

### 4.2. Reflection Engine (The Analyst)
Periodically analyzes logs to find patterns.

*   **Triggers:**
    *   **Post-Run:** Immediate reflection on failure.
    *   **Batch:** Nightly deep-dive on all trajectories.
*   **Functions:**
    *   **Failure Analysis:** "Why did step 3 fail? Missing tool? Ambiguous prompt?"
    *   **Success Clustering:** "What strategy did the top 10% of runs use?"
    *   **Strategy Extraction:** Converts clusters into natural language strategies.

### 4.3. Playbook Manager (The Librarian)
Manages the "Context Playbooks" – the evolving instruction sets for agents.

*   **Structure:**
    *   **Base Prompt:** The immutable core identity.
    *   **Strategy Layer:** Dynamic list of "Do's and Don'ts" learned over time.
    *   **Few-Shot Bank:** Curated examples of perfect executions.
*   **Operation:**
    *   **Inject:** At runtime, retrieves relevant strategies based on task embeddings.
    *   **Update:** Appends new strategies from the Reflection Engine.
    *   **Prune:** Archives obsolete or contradictory strategies (Semantic Deduplication).

## 5. Integration with Trifecta

### 5.1. ACE + UserLM (The Persona)
*   **Role:** UserLM simulates users/operators.
*   **ACE Impact:** ACE learns which tones, phrasing, and arguments work best for outreach or team coordination.
*   **Loop:** UserLM tries outreach -> ACE logs reply rate -> ACE updates "Persuasion Playbook" -> UserLM improves.

### 5.2. ACE + RND1 (The Engineer)
*   **Role:** RND1 writes code and builds systems.
*   **ACE Impact:** ACE learns common coding errors, library hallucinations, or architectural flaws.
*   **Loop:** RND1 builds DAC -> Build fails -> ACE analyzes error -> ACE adds "Library X Version Fix" to RND1's context.

### 5.3. ACE + DGM (The Evolver)
*   **Role:** DGM optimizes parameters.
*   **ACE Impact:** ACE provides the *semantic* direction for DGM.
*   **Loop:** ACE identifies a "need for speed" -> DGM translates this into T2L prompts ("Optimize for latency") -> T2L generates LoRA.

## 6. Data Schemas

### 6.1. Context Playbook Item
```yaml
id: "strat-001"
domain: "anomaly_detection"
trigger: "high_noise_environment"
strategy: "Apply rolling average filter before thresholding."
source_trace: "trace-uuid-123"
confidence_score: 0.85
created_at: "2023-10-27T10:00:00Z"
```

### 6.2. Reflection Summary
```json
{
  "period_start": "...",
  "period_end": "...",
  "analyzed_traces": 1500,
  "identified_patterns": [
    {
      "type": "failure_mode",
      "description": "Agents often hallucinate 'pandas.read_json' arguments.",
      "frequency": 0.15,
      "suggested_fix": "Add explicit pandas documentation to context."
    }
  ]
}
```

## 7. Roadmap

1.  **Phase 1: Logging:** Implement `ACEMemoryLogger` and NATS integration.
2.  **Phase 2: Reflection:** Build basic `ReflectionEngine` using RND1.
3.  **Phase 3: Playbooks:** Create `PlaybookManager` and dynamic prompt injection.
4.  **Phase 4: Closing the Loop:** Automate the feedback cycle (Log -> Reflect -> Update -> Run).
