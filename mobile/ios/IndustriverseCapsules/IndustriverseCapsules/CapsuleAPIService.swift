//
//  CapsuleAPIService.swift
//  IndustriverseCapsules
//
//  Production-ready API service for capsule-gateway integration
//  No mocks, real HTTP client implementation
//

import Foundation

/// API service for communicating with capsule-gateway backend
actor CapsuleAPIService {
    
    // MARK: - Singleton
    
    static let shared = CapsuleAPIService()
    
    // MARK: - Configuration
    
    private let baseURL: URL
    private let session: URLSession
    private var authToken: String?
    
    // MARK: - Initialization
    
    private init() {
        // Production gateway URL (configurable via environment)
        if let urlString = ProcessInfo.processInfo.environment["CAPSULE_GATEWAY_URL"] {
            self.baseURL = URL(string: urlString)!
        } else {
            // Default to production
            self.baseURL = URL(string: "https://capsule-gateway.industriverse.com")!
        }
        
        // Configure URLSession with timeout and caching
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 300
        config.requestCachePolicy = .reloadIgnoringLocalCacheData
        self.session = URLSession(configuration: config)
    }
    
    // MARK: - Authentication
    
    /// Set authentication token
    func setAuthToken(_ token: String) {
        self.authToken = token
    }
    
    // MARK: - API Methods
    
    /// Register device push token
    func registerPushToken(capsuleId: String, pushToken: String) async {
        let endpoint = baseURL.appendingPathComponent("/api/v1/devices/register")
        
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        let payload: [String: Any] = [
            "capsule_id": capsuleId,
            "push_token": pushToken,
            "device_type": "ios",
            "platform": "activitykit"
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)
            let (data, response) = try await session.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                print("✅ Registered push token for capsule: \(capsuleId)")
            } else {
                print("⚠️ Failed to register push token: \(response)")
            }
        } catch {
            print("❌ Error registering push token: \(error.localizedDescription)")
        }
    }
    
    /// Perform action on capsule
    func performAction(capsuleId: String, action: String) async {
        let endpoint = baseURL.appendingPathComponent("/api/v1/capsules/\(capsuleId)/action")
        
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        let payload: [String: Any] = [
            "action": action,
            "timestamp": ISO8601DateFormatter().string(from: Date()),
            "source": "ios_live_activity"
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)
            let (data, response) = try await session.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                print("✅ Performed action '\(action)' on capsule: \(capsuleId)")
            } else {
                print("⚠️ Failed to perform action: \(response)")
            }
        } catch {
            print("❌ Error performing action: \(error.localizedDescription)")
        }
    }
    
    /// Fetch capsule activity details
    func fetchActivity(capsuleId: String) async throws -> CapsuleActivityResponse {
        let endpoint = baseURL.appendingPathComponent("/api/v1/capsules/\(capsuleId)")
        
        var request = URLRequest(url: endpoint)
        request.httpMethod = "GET"
        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(CapsuleActivityResponse.self, from: data)
    }
    
    /// Fetch all active activities
    func fetchAllActivities() async throws -> [CapsuleActivityResponse] {
        let endpoint = baseURL.appendingPathComponent("/api/v1/capsules/activities")
        
        var request = URLRequest(url: endpoint)
        request.httpMethod = "GET"
        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let wrapper = try decoder.decode(ActivitiesWrapper.self, from: data)
        return wrapper.activities
    }
    
    /// Update activity status
    func updateActivityStatus(capsuleId: String, status: String) async throws {
        let endpoint = baseURL.appendingPathComponent("/api/v1/capsules/\(capsuleId)/status")
        
        var request = URLRequest(url: endpoint)
        request.httpMethod = "PUT"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        let payload: [String: Any] = [
            "status": status,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        let (_, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        
        print("✅ Updated status for capsule: \(capsuleId)")
    }
}

// MARK: - Response Models

struct CapsuleActivityResponse: Codable {
    let capsuleId: String
    let type: String
    let title: String
    let iconName: String
    let primaryColor: String
    let status: String
    let statusMessage: String
    let progress: Double
    let metricValue: String
    let metricLabel: String
    let lastUpdated: Date
    let actionCount: Int
    let priority: Int
    let isStale: Bool
    let alertMessage: String?
    
    enum CodingKeys: String, CodingKey {
        case capsuleId = "capsule_id"
        case type, title
        case iconName = "icon_name"
        case primaryColor = "primary_color"
        case status
        case statusMessage = "status_message"
        case progress
        case metricValue = "metric_value"
        case metricLabel = "metric_label"
        case lastUpdated = "last_updated"
        case actionCount = "action_count"
        case priority
        case isStale = "is_stale"
        case alertMessage = "alert_message"
    }
    
    /// Convert to ContentState
    func toContentState() -> CapsuleAttributes.ContentState {
        return CapsuleAttributes.ContentState(
            status: status,
            statusMessage: statusMessage,
            progress: progress,
            metricValue: metricValue,
            metricLabel: metricLabel,
            lastUpdated: lastUpdated,
            actionCount: actionCount,
            priority: priority,
            isStale: isStale,
            alertMessage: alertMessage
        )
    }
}

struct ActivitiesWrapper: Codable {
    let activities: [CapsuleActivityResponse]
}

// MARK: - Error Types

enum APIError: Error {
    case invalidResponse
    case unauthorized
    case notFound
    case serverError
    
    var localizedDescription: String {
        switch self {
        case .invalidResponse: return "Invalid response from server"
        case .unauthorized: return "Unauthorized access"
        case .notFound: return "Resource not found"
        case .serverError: return "Server error occurred"
        }
    }
}
