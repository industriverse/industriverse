# Visualization & UI Strategy: The Sovereign Avatar

**Objective:** Transform the Sovereign Daemon's outputs into an intuitive, human-centric experience. Instead of reading logs or JSON, clients receive an "On-Demand Zoom Call" from an AI Avatar that explains the week's progress, discoveries, and value delivered.

## 1. The "Sovereign Avatar" Concept
*   **Role:** The "Voice" of the Sovereign Daemon.
*   **Persona:** Professional, precise, yet visionary (think "Chief Science Officer").
*   **Function:** Narrates the `ResearchPaper`, explains complex `EnergyAtlas` visualizations, and answers high-level questions.

## 2. Automated Delivery Pipeline
1.  **Trigger:** Weekly Release or Client Email Request.
2.  **Content Gen:** `ResearchPaperGenerator` creates the scientific content.
3.  **Script Gen:** `AvatarScriptGenerator` converts the paper into a conversational script (e.g., "Hello [Client], this week we made a breakthrough in material stability...").
4.  **Video Gen:** `AvatarClient` (Mock/Argil.ai) generates the video.
5.  **Delivery:** Video is embedded in the `SovereignPortal` or emailed.

## 3. The "Holographic Boardroom" (Portal UI)
*   **Location:** `frontend/src/pages/Portal.tsx`
*   **New Component:** `SovereignAvatar.tsx`
*   **Experience:**
    *   Client logs in.
    *   Avatar appears in a "Glass Panel" overlay.
    *   Avatar narrates the weekly update.
    *   As the Avatar speaks about "Energy Spikes", the background `EnergyField` 3D visualization highlights the relevant nodes *in real-time*.

## 4. Implementation Plan
### Backend (`src/scf/visualization/`)
*   `AvatarScriptGenerator`: Logic to turn Markdown -> Speech Script.
*   `AvatarClient`: Interface for external Video Gen APIs.

### Frontend (`frontend/src/components/avatar/`)
*   `SovereignAvatar.tsx`: React component to play the video and sync with UI events.
*   `BriefingMode.tsx`: A specialized layout for the "Zoom Call" experience.

## 5. Future "Innovative" Features
*   **Interactive Interruption:** Client clicks "Wait, explain that" -> Avatar pauses and opens a detailed graph.
*   **Multi-Agent Panel:** Multiple avatars (Science Officer, CFO, Safety Officer) debating the week's results.
