import Foundation

/// Main client for Industriverse API
///
/// Provides access to all Industriverse services including thermodynamic computing,
/// DAC management, and agent ecosystem.
///
/// Example usage:
/// ```swift
/// let client = IndustriverseClient(
///     baseURL: "https://api.industriverse.io",
///     apiKey: "your-api-key"
/// )
///
/// // Thermal optimization
/// let result = try await client.thermal.sample(
///     problemType: "tsp",
///     variables: 10,
///     numSamples: 100
/// )
/// ```
public class IndustriverseClient {
    
    // MARK: - Properties
    
    /// Base URL for API requests
    public let baseURL: URL
    
    /// API key for authentication
    private let apiKey: String
    
    /// URL session for network requests
    private let session: URLSession
    
    /// Thermal sampler service client
    public lazy var thermal: ThermalSamplerClient = {
        ThermalSamplerClient(client: self)
    }()
    
    /// World model service client
    public lazy var worldModel: WorldModelClient = {
        WorldModelClient(client: self)
    }()
    
    /// Simulated snapshot service client
    public lazy var snapshot: SimulatedSnapshotClient = {
        SimulatedSnapshotClient(client: self)
    }()
    
    /// MicroAdapt Edge service client
    public lazy var microAdapt: MicroAdaptClient = {
        MicroAdaptClient(client: self)
    }()
    
    /// DAC (Deploy Anywhere Capsule) management client
    public lazy var dac: DACClient = {
        DACClient(client: self)
    }()
    
    // MARK: - Initialization
    
    /// Initialize Industriverse client
    ///
    /// - Parameters:
    ///   - baseURL: Base URL for API (default: https://api.industriverse.io)
    ///   - apiKey: API key for authentication
    ///   - session: Custom URL session (optional)
    public init(
        baseURL: String = "https://api.industriverse.io",
        apiKey: String,
        session: URLSession = .shared
    ) {
        guard let url = URL(string: baseURL) else {
            fatalError("Invalid base URL: \(baseURL)")
        }
        
        self.baseURL = url
        self.apiKey = apiKey
        self.session = session
    }
    
    // MARK: - Internal Methods
    
    /// Perform API request
    internal func request<T: Decodable>(
        method: HTTPMethod,
        path: String,
        body: Encodable? = nil
    ) async throws -> T {
        let url = baseURL.appendingPathComponent(path)
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
        }
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw IndustriverseError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw IndustriverseError.httpError(statusCode: httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(T.self, from: data)
    }
    
    /// Perform API request without response body
    internal func request(
        method: HTTPMethod,
        path: String,
        body: Encodable? = nil
    ) async throws {
        let url = baseURL.appendingPathComponent(path)
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
        }
        
        let (_, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw IndustriverseError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw IndustriverseError.httpError(statusCode: httpResponse.statusCode)
        }
    }
}

// MARK: - HTTP Method

internal enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case delete = "DELETE"
    case patch = "PATCH"
}

// MARK: - Errors

/// Industriverse SDK errors
public enum IndustriverseError: Error {
    case invalidResponse
    case httpError(statusCode: Int)
    case decodingError(Error)
    case encodingError(Error)
    case networkError(Error)
    
    public var localizedDescription: String {
        switch self {
        case .invalidResponse:
            return "Invalid response from server"
        case .httpError(let statusCode):
            return "HTTP error: \(statusCode)"
        case .decodingError(let error):
            return "Decoding error: \(error.localizedDescription)"
        case .encodingError(let error):
            return "Encoding error: \(error.localizedDescription)"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        }
    }
}
