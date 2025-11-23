import Foundation

/// Client for DAC (Deploy Anywhere Capsule) management
///
/// Provides DAC lifecycle management and execution.
public class DACClient {
    
    private let client: IndustriverseClient
    
    internal init(client: IndustriverseClient) {
        self.client = client
    }
    
    /// List available DACs
    public func list() async throws -> [DACInfo] {
        return try await client.request(
            method: .get,
            path: "/api/v1/dac/list"
        )
    }
    
    /// Get DAC details
    public func get(id: String) async throws -> DACDetails {
        return try await client.request(
            method: .get,
            path: "/api/v1/dac/\(id)"
        )
    }
    
    /// Execute DAC function
    public func execute(
        id: String,
        function: String,
        input: [String: Any]
    ) async throws -> DACExecutionResult {
        let request = DACExecutionRequest(
            function: function,
            input: input
        )
        
        return try await client.request(
            method: .post,
            path: "/api/v1/dac/\(id)/execute",
            body: request
        )
    }
    
    /// Deploy DAC to platform
    public func deploy(
        id: String,
        platform: String,
        config: [String: Any] = [:]
    ) async throws -> DeploymentResult {
        let request = DeploymentRequest(
            platform: platform,
            config: config
        )
        
        return try await client.request(
            method: .post,
            path: "/api/v1/dac/\(id)/deploy",
            body: request
        )
    }
}

// MARK: - Models

public struct DACInfo: Codable {
    public let id: String
    public let name: String
    public let description: String
    public let version: String
    public let platforms: [String]
    public let status: String
}

public struct DACDetails: Codable {
    public let id: String
    public let name: String
    public let description: String
    public let version: String
    public let platforms: [String]
    public let functions: [DACFunction]
    public let deployments: [Deployment]
    public let metadata: [String: String]
}

public struct DACFunction: Codable {
    public let name: String
    public let description: String
    public let inputSchema: [String: String]
    public let outputSchema: [String: String]
    
    enum CodingKeys: String, CodingKey {
        case name
        case description
        case inputSchema = "input_schema"
        case outputSchema = "output_schema"
    }
}

public struct Deployment: Codable {
    public let id: String
    public let platform: String
    public let status: String
    public let endpoint: String?
    public let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case platform
        case status
        case endpoint
        case createdAt = "created_at"
    }
}

public struct DACExecutionRequest: Codable {
    public let function: String
    public let input: [String: Any]
    
    public func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(function, forKey: .function)
        let jsonData = try JSONSerialization.data(withJSONObject: input)
        let jsonString = String(data: jsonData, encoding: .utf8)!
        try container.encode(jsonString, forKey: .input)
    }
    
    enum CodingKeys: String, CodingKey {
        case function
        case input
    }
}

public struct DACExecutionResult: Codable {
    public let success: Bool
    public let output: [String: Any]
    public let executionTime: Double
    public let metadata: [String: String]
    
    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        success = try container.decode(Bool.self, forKey: .success)
        let outputString = try container.decode(String.self, forKey: .output)
        let outputData = outputString.data(using: .utf8)!
        output = try JSONSerialization.jsonObject(with: outputData) as! [String: Any]
        executionTime = try container.decode(Double.self, forKey: .executionTime)
        metadata = try container.decode([String: String].self, forKey: .metadata)
    }
    
    enum CodingKeys: String, CodingKey {
        case success
        case output
        case executionTime = "execution_time"
        case metadata
    }
}

public struct DeploymentRequest: Codable {
    public let platform: String
    public let config: [String: Any]
    
    public func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(platform, forKey: .platform)
        let jsonData = try JSONSerialization.data(withJSONObject: config)
        let jsonString = String(data: jsonData, encoding: .utf8)!
        try container.encode(jsonString, forKey: .config)
    }
    
    enum CodingKeys: String, CodingKey {
        case platform
        case config
    }
}

public struct DeploymentResult: Codable {
    public let deploymentId: String
    public let status: String
    public let endpoint: String?
    public let message: String
    
    enum CodingKeys: String, CodingKey {
        case deploymentId = "deployment_id"
        case status
        case endpoint
        case message
    }
}
