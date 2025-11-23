import Foundation

/// Client for World Model service
///
/// Provides physics-based simulation using JAX.
public class WorldModelClient {
    
    private let client: IndustriverseClient
    
    internal init(client: IndustriverseClient) {
        self.client = client
    }
    
    /// Simulate physical process
    ///
    /// - Parameters:
    ///   - domain: Simulation domain (resist, plasma, thermal, etc.)
    ///   - initialState: Initial state vector
    ///   - parameters: Domain-specific parameters
    ///   - timeSteps: Number of time steps
    /// - Returns: Simulation result
    public func simulate(
        domain: String,
        initialState: [Double],
        parameters: [String: Double],
        timeSteps: Int = 100
    ) async throws -> SimulationResult {
        let request = SimulationRequest(
            domain: domain,
            initialState: initialState,
            parameters: parameters,
            timeSteps: timeSteps
        )
        
        return try await client.request(
            method: .post,
            path: "/api/v1/thermodynamic/worldmodel/simulate",
            body: request
        )
    }
    
    /// Multi-step rollout prediction
    ///
    /// - Parameters:
    ///   - domain: Simulation domain
    ///   - initialState: Initial state vector
    ///   - actions: Sequence of actions
    ///   - horizon: Prediction horizon
    /// - Returns: Rollout result
    public func rollout(
        domain: String,
        initialState: [Double],
        actions: [[Double]],
        horizon: Int
    ) async throws -> RolloutResult {
        let request = RolloutRequest(
            domain: domain,
            initialState: initialState,
            actions: actions,
            horizon: horizon
        )
        
        return try await client.request(
            method: .post,
            path: "/api/v1/thermodynamic/worldmodel/rollout?horizon=\(horizon)",
            body: request
        )
    }
    
    /// Get world model statistics
    public func statistics() async throws -> WorldModelStatistics {
        return try await client.request(
            method: .get,
            path: "/api/v1/thermodynamic/worldmodel/statistics"
        )
    }
}

// MARK: - Models

public struct SimulationRequest: Codable {
    public let domain: String
    public let initialState: [Double]
    public let parameters: [String: Double]
    public let timeSteps: Int
    
    enum CodingKeys: String, CodingKey {
        case domain
        case initialState = "initial_state"
        case parameters
        case timeSteps = "time_steps"
    }
}

public struct SimulationResult: Codable {
    public let trajectory: [[Double]]
    public let finalState: [Double]
    public let metadata: SimulationMetadata
    
    enum CodingKeys: String, CodingKey {
        case trajectory
        case finalState = "final_state"
        case metadata
    }
}

public struct SimulationMetadata: Codable {
    public let domain: String
    public let timeSteps: Int
    public let simulationTime: Double
    
    enum CodingKeys: String, CodingKey {
        case domain
        case timeSteps = "time_steps"
        case simulationTime = "simulation_time"
    }
}

public struct RolloutRequest: Codable {
    public let domain: String
    public let initialState: [Double]
    public let actions: [[Double]]
    public let horizon: Int
    
    enum CodingKeys: String, CodingKey {
        case domain
        case initialState = "initial_state"
        case actions
        case horizon
    }
}

public struct RolloutResult: Codable {
    public let predictions: [[Double]]
    public let rewards: [Double]
    public let metadata: RolloutMetadata
}

public struct RolloutMetadata: Codable {
    public let domain: String
    public let horizon: Int
    public let rolloutTime: Double
    
    enum CodingKeys: String, CodingKey {
        case domain
        case horizon
        case rolloutTime = "rollout_time"
    }
}

public struct WorldModelStatistics: Codable {
    public let totalSimulations: Int
    public let totalRollouts: Int
    public let averageSimulationTime: Double
    
    enum CodingKeys: String, CodingKey {
        case totalSimulations = "total_simulations"
        case totalRollouts = "total_rollouts"
        case averageSimulationTime = "average_simulation_time"
    }
}
