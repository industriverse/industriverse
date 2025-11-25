# UserLM Specification: The Autonomous Operator

**Based on:** "Flipping the Dialogue: Training and Evaluating User Language Models" (Arxiv: 2510.06552v1)
**Role:** The "User" in the Autonomous Discovery Loop.

## 1. Core Philosophy

UserLM is not just a chatbot; it is a **User Simulator**. Its goal is not to be helpful, but to be **realistic**, **demanding**, and **goal-oriented**. It drives the "Assistant" (RND1/Phi-4) to perform tasks by mimicking human behavior:
*   **Gradual Intent Revelation:** Does not dump all requirements at once.
*   **Imperfect Inputs:** Simulates typos, vague queries, and iterative refinement.
*   **Termination Logic:** Knows when the task is done (or failed) and ends the conversation.

## 2. Architecture

### 2.1. Inputs
*   **User Intent ($I$):** A high-level, abstract goal (e.g., "I need a Python script to parse this log file," NOT the script itself). Provided by ACE Playbooks.
*   **Conversation History ($H$):** The sequence of turns so far ($u_1, a_1, u_2, a_2, ...$).
*   **Persona/Style ($S$):** (Optional) Tone, expertise level (e.g., "Novice", "Expert").

### 2.2. The Model ($P(u_t | I, H, S)$)
*   **Training Method:** "Flipping the Dialogue".
    *   *Ideal:* Fine-tune a base model (e.g., Llama-3-8B) on human-assistant datasets (ShareGPT, WildChat) where the *user* turns are the targets.
    *   *Phase 1 (Simulated):* Use a strong LLM (Gemini/GPT-4) with a specialized system prompt that enforces the "User" role and prevents "Assistant" behavior.

### 2.3. Outputs
*   **User Turn ($u_t$):** The next utterance.
*   **Signal:** `<|endconversation|>` token if the intent $I$ is satisfied.

## 3. Integration with Trifecta

### 3.1. ACE -> UserLM
ACE provides the **Intent** and **Persona**.
*   *Example:* ACE detects a gap in "Lithium Extraction". It constructs an Intent: "Investigate novel catalysts for Li-brine separation."
*   UserLM takes this Intent and starts: "Hey, I'm looking for ways to improve lithium extraction efficiency." (Note: Vague start).

### 3.2. UserLM -> RND1
UserLM interacts with RND1 (The Builder).
*   UserLM: "The code you gave me failed on large files."
*   RND1: "I apologize. Here is the optimized version..."
*   UserLM: "Better, but now it's using too much RAM."

### 3.3. UserLM -> ACE
UserLM's satisfaction (did it output `<|endconversation|>`?) is the reward signal for ACE.

## 4. Implementation Strategy

### 4.1. The `UserLMService`
A standalone service (or class) that wraps the model.

```python
class UserLMService:
    def generate_turn(self, intent: str, history: List[Message], persona: str) -> str:
        # 1. Construct Prompt (System: "You are a user...")
        # 2. Call Model
        # 3. Check for termination token
        pass
```

### 4.2. Intent Schema (from ACE)
```json
{
  "intent_id": "uuid",
  "goal_description": "Find a material with high thermal conductivity > 400 W/mK",
  "constraints": ["Must be non-toxic", "Cost < $10/kg"],
  "success_criteria": "Simulation PRIN score > 0.8"
}
```

## 5. Roadmap

1.  **Phase 1:** Implement `UserLMService` using a prompted LLM (Simulated UserLM).
2.  **Phase 2:** Integrate with ACE Intent Schema.
3.  **Phase 3:** Fine-tune a dedicated UserLM-8B (using "Flipping the Dialogue" dataset).
