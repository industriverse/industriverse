package io.industriverse.sdk

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.json.Json

/**
 * Main client for Industriverse API
 *
 * Provides access to all Industriverse services including thermodynamic computing,
 * DAC management, and agent ecosystem.
 *
 * Example usage:
 * ```kotlin
 * val client = IndustriverseClient(
 *     baseUrl = "https://api.industriverse.io",
 *     apiKey = "your-api-key"
 * )
 *
 * // Thermal optimization
 * val result = client.thermal.sample(
 *     problemType = "tsp",
 *     variables = 10,
 *     numSamples = 100
 * )
 * ```
 */
class IndustriverseClient(
    private val baseUrl: String = "https://api.industriverse.io",
    private val apiKey: String
) {
    private val httpClient = HttpClient(CIO) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
            })
        }
    }
    
    /** Thermal sampler service client */
    val thermal = ThermalSamplerClient(this)
    
    /** World model service client */
    val worldModel = WorldModelClient(this)
    
    /** Simulated snapshot service client */
    val snapshot = SimulatedSnapshotClient(this)
    
    /** MicroAdapt Edge service client */
    val microAdapt = MicroAdaptClient(this)
    
    /** DAC management client */
    val dac = DACClient(this)
    
    internal suspend inline fun <reified T> get(path: String): T {
        return httpClient.get("$baseUrl$path") {
            header("Authorization", "Bearer $apiKey")
        }.body()
    }
    
    internal suspend inline fun <reified T, reified R> post(path: String, body: T): R {
        return httpClient.post("$baseUrl$path") {
            header("Authorization", "Bearer $apiKey")
            contentType(ContentType.Application.Json)
            setBody(body)
        }.body()
    }
    
    fun close() {
        httpClient.close()
    }
}
