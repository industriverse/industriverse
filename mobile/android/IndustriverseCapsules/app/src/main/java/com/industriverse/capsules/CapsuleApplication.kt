package com.industriverse.capsules

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import androidx.work.Configuration
import dagger.hilt.android.HiltAndroidApp
import timber.log.Timber

/**
 * Application class for Industriverse Capsules
 * Week 13: Android Native Implementation
 */
@HiltAndroidApp
class CapsuleApplication : Application(), Configuration.Provider {

    override fun onCreate() {
        super.onCreate()

        // Initialize Timber for logging
        if (BuildConfig.DEBUG_MODE) {
            Timber.plant(Timber.DebugTree())
        }

        Timber.d("Capsule Application starting...")

        // Create notification channels
        createNotificationChannels()

        Timber.d("Capsule Application initialized")
    }

    /**
     * Create notification channels for Android O+
     */
    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val notificationManager = getSystemService(NOTIFICATION_SERVICE) as NotificationManager

            // Capsule notifications channel
            val capsuleChannel = NotificationChannel(
                CHANNEL_CAPSULE_UPDATES,
                "Capsule Updates",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Notifications for capsule updates and alerts"
                enableVibration(true)
                enableLights(true)
            }

            // Foreground service channel
            val serviceChannel = NotificationChannel(
                CHANNEL_FOREGROUND_SERVICE,
                "Capsule Service",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Persistent notification for capsule service"
                setShowBadge(false)
            }

            // Low priority channel
            val lowPriorityChannel = NotificationChannel(
                CHANNEL_LOW_PRIORITY,
                "Low Priority",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Low priority capsule notifications"
                enableVibration(false)
                enableLights(false)
            }

            notificationManager.createNotificationChannels(
                listOf(capsuleChannel, serviceChannel, lowPriorityChannel)
            )

            Timber.d("Notification channels created")
        }
    }

    override fun getWorkManagerConfiguration(): Configuration {
        return Configuration.Builder()
            .setMinimumLoggingLevel(if (BuildConfig.DEBUG_MODE) android.util.Log.DEBUG else android.util.Log.ERROR)
            .build()
    }

    companion object {
        const val CHANNEL_CAPSULE_UPDATES = "capsule_updates"
        const val CHANNEL_FOREGROUND_SERVICE = "foreground_service"
        const val CHANNEL_LOW_PRIORITY = "low_priority"
    }
}
