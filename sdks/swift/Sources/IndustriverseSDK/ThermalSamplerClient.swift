import Foundation

/// Client for Thermal Sampler service
///
/// Provides energy-based optimization using thermodynamic computing.
public class ThermalSamplerClient {
    
    private let client: IndustriverseClient
    
    internal init(client: IndustriverseClient) {
        self.client = client
    }
    
    /// Sample from thermal distribution
    ///
    /// - Parameters:
    ///   - problemType: Type of optimization problem (tsp, knapsack, scheduling, etc.)
    ///   - variables: Number of variables
    ///   - constraints: Optional constraints
    ///   - numSamples: Number of samples to generate (default: 100)
    ///   - temperature: Sampling temperature (default: 1.0)
    /// - Returns: Thermal sampling result
    public func sample(
        problemType: String,
        variables: Int,
        constraints: [Constraint] = [],
        numSamples: Int = 100,
        temperature: Double = 1.0
    ) async throws -> ThermalSampleResult {
        let request = ThermalSampleRequest(
            problemType: problemType,
            variables: variables,
            constraints: constraints,
            numSamples: numSamples,
            temperature: temperature
        )
        
        return try await client.request(
            method: .post,
            path: "/api/v1/thermodynamic/thermal/sample",
            body: request
        )
    }
    
    /// Get thermal sampler statistics
    ///
    /// - Returns: Statistics about thermal sampler usage
    public func statistics() async throws -> ThermalStatistics {
        return try await client.request(
            method: .get,
            path: "/api/v1/thermodynamic/thermal/statistics"
        )
    }
}

// MARK: - Models

/// Thermal sample request
public struct ThermalSampleRequest: Codable {
    public let problemType: String
    public let variables: Int
    public let constraints: [Constraint]
    public let numSamples: Int
    public let temperature: Double
    
    enum CodingKeys: String, CodingKey {
        case problemType = "problem_type"
        case variables
        case constraints
        case numSamples = "num_samples"
        case temperature
    }
}

/// Constraint definition
public struct Constraint: Codable {
    public let type: String
    public let expression: String
    public let value: Double?
    
    public init(type: String, expression: String, value: Double? = nil) {
        self.type = type
        self.expression = expression
        self.value = value
    }
}

/// Thermal sample result
public struct ThermalSampleResult: Codable {
    public let samples: [[Double]]
    public let energies: [Double]
    public let bestSample: [Double]
    public let bestEnergy: Double
    public let convergenceHistory: [Double]
    public let metadata: ThermalMetadata
    
    enum CodingKeys: String, CodingKey {
        case samples
        case energies
        case bestSample = "best_sample"
        case bestEnergy = "best_energy"
        case convergenceHistory = "convergence_history"
        case metadata
    }
}

/// Thermal sampling metadata
public struct ThermalMetadata: Codable {
    public let problemType: String
    public let variables: Int
    public let numSamples: Int
    public let temperature: Double
    public let samplingTime: Double
    
    enum CodingKeys: String, CodingKey {
        case problemType = "problem_type"
        case variables
        case numSamples = "num_samples"
        case temperature
        case samplingTime = "sampling_time"
    }
}

/// Thermal sampler statistics
public struct ThermalStatistics: Codable {
    public let totalSamples: Int
    public let totalProblems: Int
    public let averageEnergy: Double
    public let averageSamplingTime: Double
    
    enum CodingKeys: String, CodingKey {
        case totalSamples = "total_samples"
        case totalProblems = "total_problems"
        case averageEnergy = "average_energy"
        case averageSamplingTime = "average_sampling_time"
    }
}
