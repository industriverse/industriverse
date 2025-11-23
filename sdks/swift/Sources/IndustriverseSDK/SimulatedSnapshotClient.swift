import Foundation

/// Client for Simulated Snapshot service
///
/// Provides sim/real calibration for digital twins.
public class SimulatedSnapshotClient {
    
    private let client: IndustriverseClient
    
    internal init(client: IndustriverseClient) {
        self.client = client
    }
    
    /// Store simulated snapshot
    public func store(
        snapshotType: String,
        simulatorId: String,
        realData: [String: Double],
        simulatedData: [String: Double],
        metadata: [String: String] = [:]
    ) async throws -> SnapshotStoreResult {
        let request = SnapshotStoreRequest(
            snapshotType: snapshotType,
            simulatorId: simulatorId,
            realData: realData,
            simulatedData: simulatedData,
            metadata: metadata
        )
        
        return try await client.request(
            method: .post,
            path: "/api/v1/thermodynamic/snapshot/store",
            body: request
        )
    }
    
    /// Calibrate simulator
    public func calibrate(
        snapshotId: String,
        calibrationMethod: String = "least_squares"
    ) async throws -> CalibrationResult {
        let request = CalibrationRequest(
            snapshotId: snapshotId,
            calibrationMethod: calibrationMethod
        )
        
        return try await client.request(
            method: .post,
            path: "/api/v1/thermodynamic/snapshot/calibrate",
            body: request
        )
    }
    
    /// Get snapshot statistics
    public func statistics() async throws -> SnapshotStatistics {
        return try await client.request(
            method: .get,
            path: "/api/v1/thermodynamic/snapshot/statistics"
        )
    }
}

// MARK: - Models

public struct SnapshotStoreRequest: Codable {
    public let snapshotType: String
    public let simulatorId: String
    public let realData: [String: Double]
    public let simulatedData: [String: Double]
    public let metadata: [String: String]
    
    enum CodingKeys: String, CodingKey {
        case snapshotType = "snapshot_type"
        case simulatorId = "simulator_id"
        case realData = "real_data"
        case simulatedData = "simulated_data"
        case metadata
    }
}

public struct SnapshotStoreResult: Codable {
    public let snapshotId: String
    public let stored: Bool
    
    enum CodingKeys: String, CodingKey {
        case snapshotId = "snapshot_id"
        case stored
    }
}

public struct CalibrationRequest: Codable {
    public let snapshotId: String
    public let calibrationMethod: String
    
    enum CodingKeys: String, CodingKey {
        case snapshotId = "snapshot_id"
        case calibrationMethod = "calibration_method"
    }
}

public struct CalibrationResult: Codable {
    public let correctionFactors: [String: Double]
    public let errorMetrics: [String: Double]
    public let calibrated: Bool
    
    enum CodingKeys: String, CodingKey {
        case correctionFactors = "correction_factors"
        case errorMetrics = "error_metrics"
        case calibrated
    }
}

public struct SnapshotStatistics: Codable {
    public let totalSnapshots: Int
    public let totalCalibrations: Int
    public let averageError: Double
    
    enum CodingKeys: String, CodingKey {
        case totalSnapshots = "total_snapshots"
        case totalCalibrations = "total_calibrations"
        case averageError = "average_error"
    }
}
