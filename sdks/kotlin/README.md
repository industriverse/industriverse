# Industriverse Kotlin SDK

Official Kotlin SDK for Industriverse - Deploy Anywhere Capsules (DACs) with thermodynamic computing.

## Features

- ✅ **Thermal Sampler**: Energy-based optimization
- ✅ **World Model**: Physics-based simulation using JAX
- ✅ **Simulated Snapshot**: Sim/real calibration
- ✅ **MicroAdapt Edge**: Self-evolutionary adaptive modeling
- ✅ **DAC Management**: Deploy Anywhere Capsule lifecycle
- ✅ **Coroutines**: Kotlin coroutines support
- ✅ **Type-safe**: Full Kotlin type safety with serialization
- ✅ **Multi-platform**: JVM, Android

## Installation

### Gradle (Kotlin DSL)

```kotlin
dependencies {
    implementation("io.industriverse:industriverse-sdk:1.0.0")
}
```

### Gradle (Groovy)

```groovy
dependencies {
    implementation 'io.industriverse:industriverse-sdk:1.0.0'
}
```

## Quick Start

```kotlin
import io.industriverse.sdk.*
import kotlinx.coroutines.runBlocking

fun main() = runBlocking {
    val client = IndustriverseClient(
        baseUrl = "https://api.industriverse.io",
        apiKey = "your-api-key"
    )
    
    // Thermal optimization
    val result = client.thermal.sample(
        problemType = "tsp",
        variables = 10,
        numSamples = 100
    )
    println("Best energy: ${result.bestEnergy}")
    
    // MicroAdapt forecasting
    client.microAdapt.update(
        timestamp = System.currentTimeMillis() / 1000.0,
        value = 42.5
    )
    
    val forecast = client.microAdapt.forecast(horizon = 24)
    println("Predictions: ${forecast.predictions}")
    
    client.close()
}
```

## Android Integration

```kotlin
class MainActivity : AppCompatActivity() {
    private val client = IndustriverseClient(apiKey = "your-api-key")
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        lifecycleScope.launch {
            val result = client.thermal.sample(
                problemType = "tsp",
                variables = 20,
                numSamples = 500
            )
            
            textView.text = "Best energy: ${result.bestEnergy}"
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        client.close()
    }
}
```

## Documentation

Full API documentation: https://docs.industriverse.io/kotlin

## License

MIT License
