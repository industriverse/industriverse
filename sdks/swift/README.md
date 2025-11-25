# Industriverse Swift SDK

Official Swift SDK for Industriverse - Deploy Anywhere Capsules (DACs) with thermodynamic computing.

## Features

- ✅ **Thermal Sampler**: Energy-based optimization using thermodynamic computing
- ✅ **World Model**: Physics-based simulation using JAX
- ✅ **Simulated Snapshot**: Sim/real calibration for digital twins
- ✅ **MicroAdapt Edge**: Self-evolutionary adaptive modeling (O(1) time complexity)
- ✅ **DAC Management**: Deploy Anywhere Capsule lifecycle management
- ✅ **Type-safe API**: Full Swift type safety with Codable models
- ✅ **Async/await**: Modern Swift concurrency support
- ✅ **Multi-platform**: iOS, macOS, watchOS, tvOS

## Requirements

- iOS 15.0+ / macOS 12.0+ / watchOS 8.0+ / tvOS 15.0+
- Swift 5.9+
- Xcode 15.0+

## Installation

### Swift Package Manager

Add the following to your `Package.swift`:

```swift
dependencies: [
    .package(url: "https://github.com/industriverse/industriverse-swift-sdk.git", from: "1.0.0")
]
```

Or in Xcode:
1. File > Add Package Dependencies
2. Enter: `https://github.com/industriverse/industriverse-swift-sdk.git`
3. Select version and add to your target

## Quick Start

```swift
import IndustriverseSDK

// Initialize client
let client = IndustriverseClient(
    baseURL: "https://api.industriverse.io",
    apiKey: "your-api-key"
)

// Thermal optimization
let thermalResult = try await client.thermal.sample(
    problemType: "tsp",
    variables: 10,
    numSamples: 100
)
print("Best energy: \(thermalResult.bestEnergy)")

// Physics simulation
let simResult = try await client.worldModel.simulate(
    domain: "resist",
    initialState: [1.0, 0.0, 0.0],
    parameters: ["diffusion_coeff": 0.1],
    timeSteps: 100
)
print("Final state: \(simResult.finalState)")

// Adaptive forecasting
let _ = try await client.microAdapt.update(
    timestamp: Date().timeIntervalSince1970,
    value: 42.5
)

let forecast = try await client.microAdapt.forecast(horizon: 24)
print("Predictions: \(forecast.predictions)")

// DAC execution
let dacResult = try await client.dac.execute(
    id: "my-dac",
    function: "optimize",
    input: ["target": 100]
)
print("DAC output: \(dacResult.output)")
```

## Usage Examples

### Thermal Sampler

```swift
// Traveling Salesman Problem
let tspResult = try await client.thermal.sample(
    problemType: "tsp",
    variables: 20,
    constraints: [
        Constraint(type: "distance", expression: "total < 1000")
    ],
    numSamples: 500,
    temperature: 0.5
)

print("Best route energy: \(tspResult.bestEnergy)")
print("Best route: \(tspResult.bestSample)")
print("Convergence: \(tspResult.convergenceHistory)")
```

### World Model Simulation

```swift
// Resist diffusion simulation
let resistSim = try await client.worldModel.simulate(
    domain: "resist",
    initialState: [1.0, 0.0, 0.0, 0.0],
    parameters: [
        "diffusion_coeff": 0.1,
        "reaction_rate": 0.05
    ],
    timeSteps: 200
)

print("Trajectory: \(resistSim.trajectory)")
print("Final state: \(resistSim.finalState)")

// Multi-step rollout
let rollout = try await client.worldModel.rollout(
    domain: "plasma",
    initialState: [1.0, 0.0],
    actions: [[0.1], [0.2], [0.15]],
    horizon: 50
)

print("Predictions: \(rollout.predictions)")
print("Rewards: \(rollout.rewards)")
```

### Simulated Snapshot

```swift
// Store snapshot
let snapshot = try await client.snapshot.store(
    snapshotType: "fab_sensor",
    simulatorId: "sim_v1",
    realData: ["temperature": 350.5, "pressure": 1.2],
    simulatedData: ["temperature": 348.2, "pressure": 1.25],
    metadata: ["fab": "fab3", "tool": "etch_chamber_1"]
)

print("Snapshot ID: \(snapshot.snapshotId)")

// Calibrate
let calibration = try await client.snapshot.calibrate(
    snapshotId: snapshot.snapshotId,
    calibrationMethod: "least_squares"
)

print("Correction factors: \(calibration.correctionFactors)")
print("Error metrics: \(calibration.errorMetrics)")
```

### MicroAdapt Edge

```swift
// Stream updates
for i in 0..<100 {
    let timestamp = Date().timeIntervalSince1970 + Double(i)
    let value = sin(Double(i) * 0.1) + Double.random(in: -0.1...0.1)
    
    let update = try await client.microAdapt.update(
        timestamp: timestamp,
        value: value
    )
    
    print("Regime: \(update.currentRegime), Error: \(update.predictionError)")
}

// Forecast
let forecast = try await client.microAdapt.forecast(horizon: 24)
print("24-hour forecast: \(forecast.predictions)")
print("Confidence intervals: \(forecast.confidenceIntervals)")

// Get regime info
let regime = try await client.microAdapt.regime()
print("Current regime: \(regime.currentRegime)")
print("Regime confidence: \(regime.regimeConfidence)")
print("Regime duration: \(regime.regimeDuration)")
```

### DAC Management

```swift
// List DACs
let dacs = try await client.dac.list()
for dac in dacs {
    print("\(dac.name): \(dac.status)")
}

// Get DAC details
let details = try await client.dac.get(id: "optimization-dac")
print("Functions: \(details.functions.map { $0.name })")
print("Platforms: \(details.platforms)")

// Execute DAC
let result = try await client.dac.execute(
    id: "optimization-dac",
    function: "optimize_energy",
    input: [
        "target_energy": 100.0,
        "constraints": ["max_time": 3600]
    ]
)

print("Success: \(result.success)")
print("Output: \(result.output)")
print("Execution time: \(result.executionTime)s")

// Deploy DAC
let deployment = try await client.dac.deploy(
    id: "optimization-dac",
    platform: "ios",
    config: [
        "memory_limit": 512,
        "cpu_limit": 2
    ]
)

print("Deployment ID: \(deployment.deploymentId)")
print("Status: \(deployment.status)")
if let endpoint = deployment.endpoint {
    print("Endpoint: \(endpoint)")
}
```

## Error Handling

```swift
do {
    let result = try await client.thermal.sample(
        problemType: "tsp",
        variables: 10,
        numSamples: 100
    )
    print("Success: \(result.bestEnergy)")
} catch IndustriverseError.httpError(let statusCode) {
    print("HTTP error: \(statusCode)")
} catch IndustriverseError.decodingError(let error) {
    print("Decoding error: \(error)")
} catch {
    print("Unknown error: \(error)")
}
```

## Statistics

All services provide statistics endpoints:

```swift
// Thermal sampler stats
let thermalStats = try await client.thermal.statistics()
print("Total samples: \(thermalStats.totalSamples)")
print("Average energy: \(thermalStats.averageEnergy)")

// World model stats
let worldModelStats = try await client.worldModel.statistics()
print("Total simulations: \(worldModelStats.totalSimulations)")

// Snapshot stats
let snapshotStats = try await client.snapshot.statistics()
print("Total snapshots: \(snapshotStats.totalSnapshots)")

// MicroAdapt stats
let microAdaptStats = try await client.microAdapt.statistics()
print("Total updates: \(microAdaptStats.totalUpdates)")
print("Regime changes: \(microAdaptStats.regimeChanges)")
```

## SwiftUI Integration

```swift
import SwiftUI
import IndustriverseSDK

struct ContentView: View {
    @State private var client = IndustriverseClient(
        apiKey: "your-api-key"
    )
    @State private var forecast: [Double] = []
    @State private var isLoading = false
    
    var body: some View {
        VStack {
            if isLoading {
                ProgressView("Forecasting...")
            } else {
                List(forecast.indices, id: \.self) { index in
                    Text("Hour \(index + 1): \(forecast[index], specifier: "%.2f")")
                }
            }
            
            Button("Forecast") {
                Task {
                    isLoading = true
                    do {
                        let result = try await client.microAdapt.forecast(horizon: 24)
                        forecast = result.predictions
                    } catch {
                        print("Error: \(error)")
                    }
                    isLoading = false
                }
            }
        }
    }
}
```

## Documentation

Full API documentation is available at: https://docs.industriverse.io/swift

## Support

- GitHub Issues: https://github.com/industriverse/industriverse-swift-sdk/issues
- Email: support@industriverse.io
- Slack: https://industriverse.slack.com

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.
