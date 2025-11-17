package io.industriverse.sdk

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// ============================================================================
// THERMAL SAMPLER
// ============================================================================

class ThermalSamplerClient(private val client: IndustriverseClient) {
    suspend fun sample(
        problemType: String,
        variables: Int,
        constraints: List<Constraint> = emptyList(),
        numSamples: Int = 100,
        temperature: Double = 1.0
    ): ThermalSampleResult {
        return client.post(
            "/api/v1/thermodynamic/thermal/sample",
            ThermalSampleRequest(problemType, variables, constraints, numSamples, temperature)
        )
    }
    
    suspend fun statistics(): ThermalStatistics {
        return client.get("/api/v1/thermodynamic/thermal/statistics")
    }
}

@Serializable
data class ThermalSampleRequest(
    @SerialName("problem_type") val problemType: String,
    val variables: Int,
    val constraints: List<Constraint>,
    @SerialName("num_samples") val numSamples: Int,
    val temperature: Double
)

@Serializable
data class Constraint(
    val type: String,
    val expression: String,
    val value: Double? = null
)

@Serializable
data class ThermalSampleResult(
    val samples: List<List<Double>>,
    val energies: List<Double>,
    @SerialName("best_sample") val bestSample: List<Double>,
    @SerialName("best_energy") val bestEnergy: Double,
    @SerialName("convergence_history") val convergenceHistory: List<Double>,
    val metadata: ThermalMetadata
)

@Serializable
data class ThermalMetadata(
    @SerialName("problem_type") val problemType: String,
    val variables: Int,
    @SerialName("num_samples") val numSamples: Int,
    val temperature: Double,
    @SerialName("sampling_time") val samplingTime: Double
)

@Serializable
data class ThermalStatistics(
    @SerialName("total_samples") val totalSamples: Int,
    @SerialName("total_problems") val totalProblems: Int,
    @SerialName("average_energy") val averageEnergy: Double,
    @SerialName("average_sampling_time") val averageSamplingTime: Double
)

// ============================================================================
// WORLD MODEL
// ============================================================================

class WorldModelClient(private val client: IndustriverseClient) {
    suspend fun simulate(
        domain: String,
        initialState: List<Double>,
        parameters: Map<String, Double>,
        timeSteps: Int = 100
    ): SimulationResult {
        return client.post(
            "/api/v1/thermodynamic/worldmodel/simulate",
            SimulationRequest(domain, initialState, parameters, timeSteps)
        )
    }
    
    suspend fun rollout(
        domain: String,
        initialState: List<Double>,
        actions: List<List<Double>>,
        horizon: Int
    ): RolloutResult {
        return client.post(
            "/api/v1/thermodynamic/worldmodel/rollout?horizon=$horizon",
            RolloutRequest(domain, initialState, actions, horizon)
        )
    }
    
    suspend fun statistics(): WorldModelStatistics {
        return client.get("/api/v1/thermodynamic/worldmodel/statistics")
    }
}

@Serializable
data class SimulationRequest(
    val domain: String,
    @SerialName("initial_state") val initialState: List<Double>,
    val parameters: Map<String, Double>,
    @SerialName("time_steps") val timeSteps: Int
)

@Serializable
data class SimulationResult(
    val trajectory: List<List<Double>>,
    @SerialName("final_state") val finalState: List<Double>,
    val metadata: SimulationMetadata
)

@Serializable
data class SimulationMetadata(
    val domain: String,
    @SerialName("time_steps") val timeSteps: Int,
    @SerialName("simulation_time") val simulationTime: Double
)

@Serializable
data class RolloutRequest(
    val domain: String,
    @SerialName("initial_state") val initialState: List<Double>,
    val actions: List<List<Double>>,
    val horizon: Int
)

@Serializable
data class RolloutResult(
    val predictions: List<List<Double>>,
    val rewards: List<Double>,
    val metadata: RolloutMetadata
)

@Serializable
data class RolloutMetadata(
    val domain: String,
    val horizon: Int,
    @SerialName("rollout_time") val rolloutTime: Double
)

@Serializable
data class WorldModelStatistics(
    @SerialName("total_simulations") val totalSimulations: Int,
    @SerialName("total_rollouts") val totalRollouts: Int,
    @SerialName("average_simulation_time") val averageSimulationTime: Double
)

// ============================================================================
// MICROADAPT
// ============================================================================

class MicroAdaptClient(private val client: IndustriverseClient) {
    suspend fun update(
        timestamp: Double,
        value: Double,
        features: List<Double>? = null
    ): MicroAdaptUpdateResult {
        return client.post(
            "/api/v1/thermodynamic/microadapt/update",
            MicroAdaptUpdateRequest(timestamp, value, features)
        )
    }
    
    suspend fun forecast(horizon: Int): ForecastResult {
        return client.post(
            "/api/v1/thermodynamic/microadapt/forecast",
            ForecastRequest(horizon)
        )
    }
    
    suspend fun regime(): RegimeInfo {
        return client.get("/api/v1/thermodynamic/microadapt/regime")
    }
    
    suspend fun statistics(): MicroAdaptStatistics {
        return client.get("/api/v1/thermodynamic/microadapt/statistics")
    }
}

@Serializable
data class MicroAdaptUpdateRequest(
    val timestamp: Double,
    val value: Double,
    val features: List<Double>? = null
)

@Serializable
data class MicroAdaptUpdateResult(
    val updated: Boolean,
    @SerialName("current_regime") val currentRegime: String,
    @SerialName("regime_confidence") val regimeConfidence: Double,
    @SerialName("prediction_error") val predictionError: Double
)

@Serializable
data class ForecastRequest(val horizon: Int)

@Serializable
data class ForecastResult(
    val predictions: List<Double>,
    @SerialName("confidence_intervals") val confidenceIntervals: List<List<Double>>,
    @SerialName("regime_sequence") val regimeSequence: List<String>
)

@Serializable
data class RegimeInfo(
    @SerialName("current_regime") val currentRegime: String,
    @SerialName("regime_confidence") val regimeConfidence: Double,
    @SerialName("regime_history") val regimeHistory: List<String>,
    @SerialName("regime_duration") val regimeDuration: Int
)

@Serializable
data class MicroAdaptStatistics(
    @SerialName("total_updates") val totalUpdates: Int,
    @SerialName("total_forecasts") val totalForecasts: Int,
    @SerialName("average_prediction_error") val averagePredictionError: Double,
    @SerialName("regime_changes") val regimeChanges: Int
)

// ============================================================================
// SIMULATED SNAPSHOT
// ============================================================================

class SimulatedSnapshotClient(private val client: IndustriverseClient) {
    suspend fun store(
        snapshotType: String,
        simulatorId: String,
        realData: Map<String, Double>,
        simulatedData: Map<String, Double>,
        metadata: Map<String, String> = emptyMap()
    ): SnapshotStoreResult {
        return client.post(
            "/api/v1/thermodynamic/snapshot/store",
            SnapshotStoreRequest(snapshotType, simulatorId, realData, simulatedData, metadata)
        )
    }
    
    suspend fun calibrate(
        snapshotId: String,
        calibrationMethod: String = "least_squares"
    ): CalibrationResult {
        return client.post(
            "/api/v1/thermodynamic/snapshot/calibrate",
            CalibrationRequest(snapshotId, calibrationMethod)
        )
    }
    
    suspend fun statistics(): SnapshotStatistics {
        return client.get("/api/v1/thermodynamic/snapshot/statistics")
    }
}

@Serializable
data class SnapshotStoreRequest(
    @SerialName("snapshot_type") val snapshotType: String,
    @SerialName("simulator_id") val simulatorId: String,
    @SerialName("real_data") val realData: Map<String, Double>,
    @SerialName("simulated_data") val simulatedData: Map<String, Double>,
    val metadata: Map<String, String>
)

@Serializable
data class SnapshotStoreResult(
    @SerialName("snapshot_id") val snapshotId: String,
    val stored: Boolean
)

@Serializable
data class CalibrationRequest(
    @SerialName("snapshot_id") val snapshotId: String,
    @SerialName("calibration_method") val calibrationMethod: String
)

@Serializable
data class CalibrationResult(
    @SerialName("correction_factors") val correctionFactors: Map<String, Double>,
    @SerialName("error_metrics") val errorMetrics: Map<String, Double>,
    val calibrated: Boolean
)

@Serializable
data class SnapshotStatistics(
    @SerialName("total_snapshots") val totalSnapshots: Int,
    @SerialName("total_calibrations") val totalCalibrations: Int,
    @SerialName("average_error") val averageError: Double
)

// ============================================================================
// DAC
// ============================================================================

class DACClient(private val client: IndustriverseClient) {
    suspend fun list(): List<DACInfo> {
        return client.get("/api/v1/dac/list")
    }
    
    suspend fun get(id: String): DACDetails {
        return client.get("/api/v1/dac/$id")
    }
}

@Serializable
data class DACInfo(
    val id: String,
    val name: String,
    val description: String,
    val version: String,
    val platforms: List<String>,
    val status: String
)

@Serializable
data class DACDetails(
    val id: String,
    val name: String,
    val description: String,
    val version: String,
    val platforms: List<String>,
    val functions: List<DACFunction>,
    val deployments: List<Deployment>,
    val metadata: Map<String, String>
)

@Serializable
data class DACFunction(
    val name: String,
    val description: String,
    @SerialName("input_schema") val inputSchema: Map<String, String>,
    @SerialName("output_schema") val outputSchema: Map<String, String>
)

@Serializable
data class Deployment(
    val id: String,
    val platform: String,
    val status: String,
    val endpoint: String?,
    @SerialName("created_at") val createdAt: String
)
