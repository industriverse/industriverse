import demoRegistry from '../src/demos/demo_registry.json' with { type: "json" };
import packARunner from '../src/demos/pack_a_runner.js';
import packBRunner from '../src/demos/pack_b_runner.js';
import packCRunner from '../src/demos/pack_c_runner.js';
import packDRunner from '../src/demos/pack_d_runner.js';
import packERunner from '../src/demos/pack_e_runner.js';

async function runTestSuite() {
    console.log("--- Testing 50-Demo Investor Suite ---");

    let totalDemos = 0;
    let passedDemos = 0;
    let failedDemos = 0;

    const runners = {
        'pack_a': packARunner,
        'pack_b': packBRunner,
        'pack_c': packCRunner,
        'pack_d': packDRunner,
        'pack_e': packERunner
    };

    // Override delay to speed up tests
    for (const key in runners) {
        runners[key].delay = () => Promise.resolve();
    }

    for (const pack of demoRegistry.packs) {
        console.log(`\nTesting ${pack.title}...`);
        const runner = runners[pack.id];

        if (!runner) {
            console.error(`❌ No runner found for ${pack.id}`);
            continue;
        }

        for (const demo of pack.demos) {
            totalDemos++;
            process.stdout.write(`  [${demo.id}] ${demo.title}... `);

            try {
                let logCount = 0;
                await runner.run(demo.id, demo.config, (msg) => {
                    logCount++;
                });

                if (logCount > 0) {
                    console.log("✅ PASS");
                    passedDemos++;
                } else {
                    console.log("❌ FAIL (No Logs)");
                    failedDemos++;
                }
            } catch (e) {
                console.log(`❌ FAIL (${e.message})`);
                failedDemos++;
            }
        }
    }

    console.log("\n--- Test Summary ---");
    console.log(`Total: ${totalDemos}`);
    console.log(`Passed: ${passedDemos}`);
    console.log(`Failed: ${failedDemos}`);

    if (failedDemos === 0) {
        console.log("✅ ALL SYSTEMS GO.");
        process.exit(0);
    } else {
        console.log("❌ SOME DEMOS FAILED.");
        process.exit(1);
    }
}

runTestSuite();
