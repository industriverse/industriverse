# Research Automation Strategy (RDR Integration)

**Objective:** Automate the ingestion, synthesis, and application of scientific knowledge (PDFs, Papers, RDR) to fuel the RND1 "Builder" engine.

## 1. The Pipeline
We will extend the **Universal Ingestion Engine** to handle unstructured scientific data.

`[PDF/RDR Source] --> [PDF Parser] --> [Text Chunker] --> [LLM Summarizer] --> [Knowledge Graph] --> [RND1 Context]`

## 2. Components

### 2.1. Ingestion Source (RDR)
*   **Target:** Research Data Repositories (RDR), ArXiv, Corporate Knowledge Bases.
*   **Format:** PDF, LaTeX, JSON.

### 2.2. Parsing Layer
*   **Tool:** `pypdf` or `unstructured`.
*   **Action:** Extract text, tables, and figures.
*   **Metadata:** Title, Authors, Date, DOI.

### 2.3. Synthesis Layer (The "Researcher" Persona)
*   **Model:** UserLM (configured as "Researcher").
*   **Prompt:** "Extract key physical constants, equations, and experimental results from this paper."
*   **Output:** Structured JSON (e.g., `{"equation": "E=mc^2", "context": "Relativity"}`).

### 2.4. Integration with Trifecta
*   **ACE**: Stores the synthesized knowledge in the "Long-Term Memory".
*   **RND1**: Queries this memory when generating hypotheses.
    *   *Example:* "Goal: Optimize Superconductor." -> RND1 queries memory for "latest Tc records" -> Generates simulation based on new paper.

## 3. Implementation Plan (Script)
We will create `scripts/ingest_research_pdfs.py` to:
1.  Scan a directory for PDFs.
2.  Parse text.
3.  (Mock) Call LLM to summarize.
4.  Store in a local JSON "Knowledge Base".

## 4. Future State
*   **Auto-Review**: System automatically reads new ArXiv papers daily.
*   **Hypothesis Evolution**: System proposes new experiments based on reading literature.
