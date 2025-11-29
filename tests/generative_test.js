import GenerativeGlyphEngine from '../src/utils/GenerativeGlyphEngine.js';

async function runTest() {
    console.log("=== Generative Glyph Engine Verification ===\n");

    const prompts = [
        "Make a bracket",
        "Make a lightweight bracket",
        "Make a fast gear"
    ];

    for (const prompt of prompts) {
        console.log(`Prompt: "${prompt}"`);
        const result = await GenerativeGlyphEngine.generate(prompt);

        if (result.error) {
            console.error(`Error: ${result.error}`);
        } else {
            console.log(`Generated Sequence: ${JSON.stringify(result.glyphs)}`);
            console.log(`Energy Estimate: ${result.energy_estimate}`);
            console.log(`Reasoning: ${result.reasoning}`);

            // Validation Logic
            if (prompt.includes("lightweight") && !result.glyphs.includes("⊽0.1")) {
                console.error("FAIL: Did not optimize for lightweight!");
            }
            if (prompt.includes("fast") && !result.glyphs.includes("⊽0.5")) {
                console.error("FAIL: Did not optimize for speed!");
            }
        }
        console.log("-".repeat(40));
    }
}

runTest();
