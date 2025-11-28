package com.industriverse.capsules.service

import android.app.Service
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import androidx.core.app.ServiceCompat
import com.industriverse.capsules.data.models.Capsule
import com.industriverse.capsules.data.models.CapsuleUpdate
import com.industriverse.capsules.data.models.UpdateEventType
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.launch
import timber.log.Timber
import javax.inject.Inject

/**
 * Capsule Foreground Service
 * Week 13 Day 3-4: Foreground service implementation
 *
 * This service:
 * - Maintains persistent WebSocket connection to Capsule Gateway
 * - Shows persistent notification in notification tray
 * - Handles real-time capsule updates
 * - Manages capsule notifications
 * - Survives app termination
 * - Handles Doze mode and battery optimization
 */
@AndroidEntryPoint
class CapsuleService : Service() {

    @Inject
    lateinit var webSocketManager: WebSocketManager

    @Inject
    lateinit var notificationManager: CapsuleNotificationManager

    private val serviceScope = CoroutineScope(Dispatchers.Main + Job())
    private var isServiceRunning = false

    override fun onCreate() {
        super.onCreate()
        Timber.d("CapsuleService onCreate")
        isServiceRunning = true
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Timber.d("CapsuleService onStartCommand: action=${intent?.action}")

        when (intent?.action) {
            ACTION_START_SERVICE -> startForegroundService()
            ACTION_STOP_SERVICE -> stopForegroundService()
            ACTION_EXECUTE_ACTION -> handleActionExecution(intent)
            else -> startForegroundService()
        }

        // START_STICKY ensures service is restarted if killed by system
        return START_STICKY
    }

    /**
     * Start foreground service with persistent notification
     */
    private fun startForegroundService() {
        if (!isServiceRunning) return

        Timber.d("Starting capsule foreground service")

        // Create and show foreground notification
        val notification = notificationManager.createForegroundNotification(0)

        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                ServiceCompat.startForeground(
                    this,
                    CapsuleNotificationManager.FOREGROUND_SERVICE_NOTIFICATION_ID,
                    notification,
                    ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
                )
            } else {
                startForeground(
                    CapsuleNotificationManager.FOREGROUND_SERVICE_NOTIFICATION_ID,
                    notification
                )
            }
        } catch (e: Exception) {
            Timber.e(e, "Failed to start foreground service")
            stopSelf()
            return
        }

        // Connect to WebSocket
        connectWebSocket()

        // Observe capsule updates
        observeCapsuleUpdates()
    }

    /**
     * Stop foreground service
     */
    private fun stopForegroundService() {
        Timber.d("Stopping capsule foreground service")

        webSocketManager.disconnect()
        notificationManager.cancelAllCapsuleNotifications()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            stopForeground(STOP_FOREGROUND_REMOVE)
        } else {
            @Suppress("DEPRECATION")
            stopForeground(true)
        }

        stopSelf()
    }

    /**
     * Connect to WebSocket
     */
    private fun connectWebSocket() {
        // In production, get these from secure storage
        val userId = getUserId()
        val token = getAuthToken()

        if (userId.isEmpty() || token.isEmpty()) {
            Timber.w("User not authenticated, cannot connect to WebSocket")
            return
        }

        webSocketManager.connect(userId, token)
    }

    /**
     * Observe capsule updates and manage notifications
     */
    private fun observeCapsuleUpdates() {
        // Observe both connection state and capsule updates
        serviceScope.launch {
            combine(
                webSocketManager.connectionState,
                webSocketManager.activeCapsules,
                webSocketManager.capsuleUpdates
            ) { connectionState, activeCapsules, update ->
                Triple(connectionState, activeCapsules, update)
            }.collect { (connectionState, activeCapsules, update) ->
                handleCapsuleState(connectionState, activeCapsules, update)
            }
        }
    }

    /**
     * Handle capsule state changes
     */
    private fun handleCapsuleState(
        connectionState: ConnectionState,
        activeCapsules: List<Capsule>,
        update: CapsuleUpdate?
    ) {
        // Update foreground notification with capsule count
        val notification = notificationManager.createForegroundNotification(activeCapsules.size)
        notificationManager.notificationManager.notify(
            CapsuleNotificationManager.FOREGROUND_SERVICE_NOTIFICATION_ID,
            notification
        )

        // Handle individual capsule updates
        update?.let {
            handleCapsuleUpdate(it)
        }

        // Show summary notification if multiple capsules
        if (activeCapsules.size > 3) {
            notificationManager.showSummaryNotification(activeCapsules)
        }

        // Log connection state changes
        when (connectionState) {
            is ConnectionState.Connected -> Timber.d("Connected to Capsule Gateway")
            is ConnectionState.Connecting -> Timber.d("Connecting to Capsule Gateway...")
            is ConnectionState.Disconnected -> Timber.w("Disconnected from Capsule Gateway")
            is ConnectionState.Error -> Timber.e("WebSocket error: ${connectionState.message}")
        }
    }

    /**
     * Handle individual capsule update
     */
    private fun handleCapsuleUpdate(update: CapsuleUpdate) {
        Timber.d("Handling capsule update: ${update.eventType} for ${update.capsuleId}")

        when (update.eventType) {
            UpdateEventType.CREATED -> {
                // New capsule created, show notification
                update.capsule?.let { capsule ->
                    if (capsule.requiresAttention()) {
                        notificationManager.showCapsuleNotification(capsule)
                    }
                }
            }
            UpdateEventType.UPDATED, UpdateEventType.STATE_CHANGED -> {
                // Capsule updated, update notification
                update.capsule?.let { capsule ->
                    if (capsule.requiresAttention()) {
                        notificationManager.updateCapsuleNotification(capsule)
                    } else {
                        notificationManager.cancelCapsuleNotification(capsule.capsuleId)
                    }
                }
            }
            UpdateEventType.DELETED -> {
                // Capsule deleted, cancel notification
                notificationManager.cancelCapsuleNotification(update.capsuleId)
            }
            UpdateEventType.ACTION_COMPLETED -> {
                // Action completed, might dismiss capsule
                update.capsule?.let { capsule ->
                    if (capsule.state == com.industriverse.capsules.data.models.CapsuleState.COMPLETED ||
                        capsule.state == com.industriverse.capsules.data.models.CapsuleState.DISMISSED
                    ) {
                        notificationManager.cancelCapsuleNotification(capsule.capsuleId)
                    }
                }
            }
        }
    }

    /**
     * Handle action execution from notification
     */
    private fun handleActionExecution(intent: Intent) {
        val capsuleId = intent.getStringExtra(EXTRA_CAPSULE_ID) ?: return
        val actionId = intent.getStringExtra(EXTRA_ACTION_ID) ?: return

        Timber.d("Executing action $actionId on capsule $capsuleId")
        webSocketManager.executeAction(capsuleId, actionId)
    }

    /**
     * Get user ID (from preferences in production)
     */
    private fun getUserId(): String {
        // TODO: Get from DataStore or SharedPreferences
        return "user123" // Placeholder
    }

    /**
     * Get auth token (from secure storage in production)
     */
    private fun getAuthToken(): String {
        // TODO: Get from encrypted storage
        return "token123" // Placeholder
    }

    override fun onBind(intent: Intent?): IBinder? {
        // This is not a bound service
        return null
    }

    override fun onDestroy() {
        Timber.d("CapsuleService onDestroy")
        isServiceRunning = false
        serviceScope.cancel()
        webSocketManager.disconnect()
        super.onDestroy()
    }

    /**
     * Handle task removed (app swiped away)
     */
    override fun onTaskRemoved(rootIntent: Intent?) {
        super.onTaskRemoved(rootIntent)
        Timber.d("Task removed, service will continue running")
        // Service continues running even when app is swiped away
    }

    companion object {
        const val ACTION_START_SERVICE = "com.industriverse.capsules.START_SERVICE"
        const val ACTION_STOP_SERVICE = "com.industriverse.capsules.STOP_SERVICE"
        const val ACTION_EXECUTE_ACTION = "com.industriverse.capsules.EXECUTE_ACTION"

        const val EXTRA_CAPSULE_ID = "capsule_id"
        const val EXTRA_ACTION_ID = "action_id"
    }
}
