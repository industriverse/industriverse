# Slice100k Value Extraction Strategy: The Industrial Glyph Language

## 1. The Data Reality: Binary G-code (.bgcode)
Our inspection reveals that Slice100k uses **Binary G-code (.bgcode)**. This is a compressed format introduced by Prusa.
*   **Challenge:** Standard text parsers won't work.
*   **Opportunity:** This binary format is already "tokenized." It is closer to a machine language than raw ASCII.
*   **Action:** We will build a **Binary Glyph Decoder** that treats these binary blocks as the fundamental "words" of our Industrial Language.

## 2. Value Extraction Layers

### Layer 1: The Energy Voxel (Thermodynamics)
*   **Input:** Decoded G-code (Movement + Extrusion).
*   **Process:** Map every `G1` vector to a generic energy cost ($E = P \times t$).
*   **Output:** A 3D Energy Density Map ($J/mm^3$).
*   **Value:** "Predict the energy cost of a shape before printing it."

### Layer 2: The Industrial Glyph (Linguistics)
*   **Concept:** G-code is a language.
    *   *Phonemes:* Individual commands (`G1`, `M104`).
    *   *Words:* Functional blocks (e.g., "Infill Pattern", "Perimeter Loop").
    *   *Sentences:* Complete layers.
*   **Innovation:** We will train a **Transformer (SliceLM)** to learn the grammar of these Glyphs.
*   **Value:** "Text-to-Factory" - Speak a design, and the AI generates the Glyphs.

### Layer 3: The Geometry-Energy Bridge (Multimodal)
*   **Input:** STLs (Geometry) + G-code (Energy).
*   **Process:** Train a model to predict the *Energy Voxel* from the *Geometry Voxel*.
*   **Value:** Instant thermodynamic auditing of CAD files without slicing.

## 3. Immediate Next Steps
1.  **Decoder:** Implement a `.bgcode` to `.gcode` converter (using `libbgcode` or reverse-engineering the header).
2.  **Atlas:** Process the first 1,000 files to build a "Mini Energy Atlas."
3.  **Glyph Tokenizer:** Create a tokenizer that maps binary blocks to integer tokens for LLM training.

## 4. Vision Connection
This dataset is the **Rosetta Stone** for the Industriverse. It translates "Human Intent" (CAD) into "Machine Action" (Energy). By mastering this translation, we enable the **Self-Replicating Machine**.
