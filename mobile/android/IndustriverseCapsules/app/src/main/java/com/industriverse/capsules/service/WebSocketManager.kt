package com.industriverse.capsules.service

import com.google.gson.Gson
import com.industriverse.capsules.BuildConfig
import com.industriverse.capsules.data.models.Capsule
import com.industriverse.capsules.data.models.CapsuleUpdate
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import timber.log.Timber
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

/**
 * WebSocket Manager for real-time capsule updates
 * Week 13 Day 3-4: WebSocket real-time connection
 *
 * Handles:
 * - WebSocket connection to Capsule Gateway
 * - Automatic reconnection with exponential backoff
 * - Heartbeat/ping-pong mechanism
 * - Message parsing and distribution
 */
@Singleton
class WebSocketManager @Inject constructor(
    private val gson: Gson
) {
    private var webSocket: WebSocket? = null
    private val scope = CoroutineScope(Dispatchers.IO + Job())

    // Connection state
    private val _connectionState = MutableStateFlow<ConnectionState>(ConnectionState.Disconnected)
    val connectionState: StateFlow<ConnectionState> = _connectionState

    // Capsule updates
    private val _capsuleUpdates = MutableStateFlow<CapsuleUpdate?>(null)
    val capsuleUpdates: StateFlow<CapsuleUpdate?> = _capsuleUpdates

    // Active capsules
    private val _activeCapsules = MutableStateFlow<List<Capsule>>(emptyList())
    val activeCapsules: StateFlow<List<Capsule>> = _activeCapsules

    // Reconnection
    private var reconnectJob: Job? = null
    private var reconnectAttempts = 0
    private val maxReconnectAttempts = 10
    private val baseReconnectDelay = 1000L // 1 second

    // Heartbeat
    private var heartbeatJob: Job? = null
    private val heartbeatInterval = 30000L // 30 seconds

    // OkHttp client
    private val client = OkHttpClient.Builder()
        .pingInterval(30, TimeUnit.SECONDS)
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(0, TimeUnit.SECONDS) // No timeout for reading
        .writeTimeout(10, TimeUnit.SECONDS)
        .build()

    /**
     * Connect to WebSocket
     */
    fun connect(userId: String, token: String) {
        Timber.d("Connecting to WebSocket for user: $userId")

        if (_connectionState.value == ConnectionState.Connected) {
            Timber.w("Already connected to WebSocket")
            return
        }

        _connectionState.value = ConnectionState.Connecting

        val url = "${BuildConfig.CAPSULE_GATEWAY_URL}/ws?userId=$userId&token=$token"
        val request = Request.Builder()
            .url(url)
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                Timber.d("WebSocket connected")
                _connectionState.value = ConnectionState.Connected
                reconnectAttempts = 0
                startHeartbeat()

                // Send initial subscribe message
                sendMessage(
                    mapOf(
                        "type" to "subscribe",
                        "userId" to userId
                    )
                )
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                Timber.d("WebSocket message received: ${text.take(100)}")
                handleMessage(text)
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                Timber.d("WebSocket closing: $code - $reason")
                webSocket.close(1000, null)
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                Timber.d("WebSocket closed: $code - $reason")
                _connectionState.value = ConnectionState.Disconnected
                stopHeartbeat()
                scheduleReconnect(userId, token)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Timber.e(t, "WebSocket failure: ${response?.message}")
                _connectionState.value = ConnectionState.Error(t.message ?: "Unknown error")
                stopHeartbeat()
                scheduleReconnect(userId, token)
            }
        })
    }

    /**
     * Disconnect from WebSocket
     */
    fun disconnect() {
        Timber.d("Disconnecting from WebSocket")
        stopHeartbeat()
        reconnectJob?.cancel()
        webSocket?.close(1000, "Client disconnect")
        webSocket = null
        _connectionState.value = ConnectionState.Disconnected
    }

    /**
     * Send message to WebSocket
     */
    fun sendMessage(message: Map<String, Any>) {
        val json = gson.toJson(message)
        Timber.d("Sending WebSocket message: $json")
        webSocket?.send(json)
    }

    /**
     * Handle incoming WebSocket message
     */
    private fun handleMessage(text: String) {
        try {
            val message = gson.fromJson(text, Map::class.java)
            val type = message["type"] as? String

            when (type) {
                "capsule_update" -> {
                    val update = gson.fromJson(text, CapsuleUpdate::class.java)
                    _capsuleUpdates.value = update
                    updateActiveCapsules(update)
                }
                "capsule_list" -> {
                    @Suppress("UNCHECKED_CAST")
                    val capsules = (message["capsules"] as? List<Map<String, Any>>)?.map {
                        gson.fromJson(gson.toJson(it), Capsule::class.java)
                    } ?: emptyList()
                    _activeCapsules.value = capsules
                    Timber.d("Received ${capsules.size} active capsules")
                }
                "heartbeat" -> {
                    // Respond to heartbeat
                    sendMessage(mapOf("type" to "heartbeat_ack"))
                }
                "error" -> {
                    val error = message["message"] as? String ?: "Unknown error"
                    Timber.e("WebSocket error: $error")
                    _connectionState.value = ConnectionState.Error(error)
                }
                else -> {
                    Timber.d("Unknown message type: $type")
                }
            }
        } catch (e: Exception) {
            Timber.e(e, "Error handling WebSocket message")
        }
    }

    /**
     * Update active capsules list based on update
     */
    private fun updateActiveCapsules(update: CapsuleUpdate) {
        val currentCapsules = _activeCapsules.value.toMutableList()

        when (update.eventType) {
            com.industriverse.capsules.data.models.UpdateEventType.CREATED -> {
                update.capsule?.let { currentCapsules.add(it) }
            }
            com.industriverse.capsules.data.models.UpdateEventType.UPDATED,
            com.industriverse.capsules.data.models.UpdateEventType.STATE_CHANGED,
            com.industriverse.capsules.data.models.UpdateEventType.ACTION_COMPLETED -> {
                val index = currentCapsules.indexOfFirst { it.capsuleId == update.capsuleId }
                if (index != -1 && update.capsule != null) {
                    currentCapsules[index] = update.capsule
                }
            }
            com.industriverse.capsules.data.models.UpdateEventType.DELETED -> {
                currentCapsules.removeAll { it.capsuleId == update.capsuleId }
            }
        }

        _activeCapsules.value = currentCapsules
    }

    /**
     * Start heartbeat mechanism
     */
    private fun startHeartbeat() {
        heartbeatJob?.cancel()
        heartbeatJob = scope.launch {
            while (true) {
                delay(heartbeatInterval)
                if (_connectionState.value == ConnectionState.Connected) {
                    sendMessage(mapOf("type" to "ping"))
                }
            }
        }
    }

    /**
     * Stop heartbeat mechanism
     */
    private fun stopHeartbeat() {
        heartbeatJob?.cancel()
        heartbeatJob = null
    }

    /**
     * Schedule reconnection with exponential backoff
     */
    private fun scheduleReconnect(userId: String, token: String) {
        if (reconnectAttempts >= maxReconnectAttempts) {
            Timber.e("Max reconnect attempts reached")
            _connectionState.value = ConnectionState.Error("Max reconnect attempts reached")
            return
        }

        reconnectJob?.cancel()
        reconnectJob = scope.launch {
            val delay = baseReconnectDelay * (1 shl reconnectAttempts) // Exponential backoff
            Timber.d("Reconnecting in ${delay}ms (attempt ${reconnectAttempts + 1})")
            reconnectAttempts++

            delay(delay)

            if (_connectionState.value != ConnectionState.Connected) {
                connect(userId, token)
            }
        }
    }

    /**
     * Request capsule list refresh
     */
    fun refreshCapsules() {
        Timber.d("Requesting capsule list refresh")
        sendMessage(mapOf("type" to "get_capsules"))
    }

    /**
     * Execute capsule action
     */
    fun executeAction(capsuleId: String, actionId: String) {
        Timber.d("Executing action $actionId on capsule $capsuleId")
        sendMessage(
            mapOf(
                "type" to "execute_action",
                "capsule_id" to capsuleId,
                "action_id" to actionId
            )
        )
    }
}

/**
 * WebSocket connection state
 */
sealed class ConnectionState {
    object Disconnected : ConnectionState()
    object Connecting : ConnectionState()
    object Connected : ConnectionState()
    data class Error(val message: String) : ConnectionState()
}
