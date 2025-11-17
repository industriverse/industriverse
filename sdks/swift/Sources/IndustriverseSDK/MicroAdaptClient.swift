import Foundation

/// Client for MicroAdapt Edge service
///
/// Provides self-evolutionary adaptive modeling with O(1) time complexity.
public class MicroAdaptClient {
    
    private let client: IndustriverseClient
    
    internal init(client: IndustriverseClient) {
        self.client = client
    }
    
    /// Update model with new observation
    ///
    /// - Parameters:
    ///   - timestamp: Observation timestamp
    ///   - value: Observed value
    ///   - features: Optional feature vector
    /// - Returns: Update result with regime information
    public func update(
        timestamp: Double,
        value: Double,
        features: [Double]? = nil
    ) async throws -> MicroAdaptUpdateResult {
        let request = MicroAdaptUpdateRequest(
            timestamp: timestamp,
            value: value,
            features: features
        )
        
        return try await client.request(
            method: .post,
            path: "/api/v1/thermodynamic/microadapt/update",
            body: request
        )
    }
    
    /// Forecast future values
    ///
    /// - Parameter horizon: Forecast horizon (number of steps)
    /// - Returns: Forecast result
    public func forecast(horizon: Int) async throws -> ForecastResult {
        let request = ForecastRequest(horizon: horizon)
        
        return try await client.request(
            method: .post,
            path: "/api/v1/thermodynamic/microadapt/forecast",
            body: request
        )
    }
    
    /// Get current regime information
    public func regime() async throws -> RegimeInfo {
        return try await client.request(
            method: .get,
            path: "/api/v1/thermodynamic/microadapt/regime"
        )
    }
    
    /// Get MicroAdapt statistics
    public func statistics() async throws -> MicroAdaptStatistics {
        return try await client.request(
            method: .get,
            path: "/api/v1/thermodynamic/microadapt/statistics"
        )
    }
}

// MARK: - Models

public struct MicroAdaptUpdateRequest: Codable {
    public let timestamp: Double
    public let value: Double
    public let features: [Double]?
}

public struct MicroAdaptUpdateResult: Codable {
    public let updated: Bool
    public let currentRegime: String
    public let regimeConfidence: Double
    public let predictionError: Double
    
    enum CodingKeys: String, CodingKey {
        case updated
        case currentRegime = "current_regime"
        case regimeConfidence = "regime_confidence"
        case predictionError = "prediction_error"
    }
}

public struct ForecastRequest: Codable {
    public let horizon: Int
}

public struct ForecastResult: Codable {
    public let predictions: [Double]
    public let confidenceIntervals: [[Double]]
    public let regimeSequence: [String]
    
    enum CodingKeys: String, CodingKey {
        case predictions
        case confidenceIntervals = "confidence_intervals"
        case regimeSequence = "regime_sequence"
    }
}

public struct RegimeInfo: Codable {
    public let currentRegime: String
    public let regimeConfidence: Double
    public let regimeHistory: [String]
    public let regimeDuration: Int
    
    enum CodingKeys: String, CodingKey {
        case currentRegime = "current_regime"
        case regimeConfidence = "regime_confidence"
        case regimeHistory = "regime_history"
        case regimeDuration = "regime_duration"
    }
}

public struct MicroAdaptStatistics: Codable {
    public let totalUpdates: Int
    public let totalForecasts: Int
    public let averagePredictionError: Double
    public let regimeChanges: Int
    
    enum CodingKeys: String, CodingKey {
        case totalUpdates = "total_updates"
        case totalForecasts = "total_forecasts"
        case averagePredictionError = "average_prediction_error"
        case regimeChanges = "regime_changes"
    }
}
