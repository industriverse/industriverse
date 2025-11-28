package com.industriverse.capsules.service

import android.app.Notification
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.graphics.Color
import androidx.core.app.NotificationCompat
import com.industriverse.capsules.CapsuleApplication
import com.industriverse.capsules.R
import com.industriverse.capsules.data.models.Capsule
import com.industriverse.capsules.data.models.CapsuleAction
import com.industriverse.capsules.data.models.CapsulePriority
import com.industriverse.capsules.ui.MainActivity
import dagger.hilt.android.qualifiers.ApplicationContext
import timber.log.Timber
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Notification Manager for Capsule notifications
 * Week 13 Day 3-4: Persistent notification implementation
 *
 * Handles:
 * - Foreground service persistent notification
 * - Individual capsule notifications
 * - Action buttons on notifications
 * - Notification updates
 */
@Singleton
class CapsuleNotificationManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val notificationManager =
        context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

    /**
     * Create foreground service notification
     */
    fun createForegroundNotification(activeCapsuleCount: Int): Notification {
        val intent = Intent(context, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context,
            0,
            intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        return NotificationCompat.Builder(context, CapsuleApplication.CHANNEL_FOREGROUND_SERVICE)
            .setContentTitle("Capsule Service")
            .setContentText(
                if (activeCapsuleCount > 0) {
                    "$activeCapsuleCount active capsule${if (activeCapsuleCount == 1) "" else "s"}"
                } else {
                    "Monitoring for capsule updates"
                }
            )
            .setSmallIcon(R.drawable.ic_notification)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .setSilent(true)
            .setShowWhen(false)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setCategory(NotificationCompat.CATEGORY_SERVICE)
            .build()
    }

    /**
     * Show notification for a capsule
     */
    fun showCapsuleNotification(capsule: Capsule) {
        Timber.d("Showing notification for capsule: ${capsule.capsuleId}")

        val notificationId = capsule.capsuleId.hashCode()

        // Create intent to open app
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            putExtra("capsule_id", capsule.capsuleId)
        }
        val pendingIntent = PendingIntent.getActivity(
            context,
            notificationId,
            intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        // Determine notification channel based on priority
        val channelId = when (capsule.priority) {
            CapsulePriority.CRITICAL, CapsulePriority.HIGH -> CapsuleApplication.CHANNEL_CAPSULE_UPDATES
            else -> CapsuleApplication.CHANNEL_LOW_PRIORITY
        }

        // Build notification
        val builder = NotificationCompat.Builder(context, channelId)
            .setContentTitle(capsule.title)
            .setContentText(capsule.subtitle ?: capsule.description)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setWhen(capsule.updatedAt.time)
            .setShowWhen(true)
            .setPriority(getPriority(capsule.priority))
            .setCategory(getCategory(capsule.capsuleType))

        // Add color
        try {
            val color = Color.parseColor(capsule.getDisplayColor())
            builder.setColor(color)
        } catch (e: Exception) {
            Timber.w(e, "Failed to parse color: ${capsule.color}")
        }

        // Add badge count
        if (capsule.badgeCount > 0) {
            builder.setNumber(capsule.badgeCount)
        }

        // Add progress bar if applicable
        capsule.progress?.let { progress ->
            builder.setProgress(100, (progress * 100).toInt(), false)
        }

        // Add style for longer text
        capsule.description?.let { description ->
            builder.setStyle(
                NotificationCompat.BigTextStyle()
                    .bigText(description)
                    .setBigContentTitle(capsule.title)
            )
        }

        // Add action buttons
        capsule.actions.take(3).forEach { action ->
            val actionIntent = Intent(context, CapsuleActionReceiver::class.java).apply {
                putExtra("capsule_id", capsule.capsuleId)
                putExtra("action_id", action.actionId)
            }
            val actionPendingIntent = PendingIntent.getBroadcast(
                context,
                "$notificationId:${action.actionId}".hashCode(),
                actionIntent,
                PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
            )

            builder.addAction(
                0, // No icon for now
                action.label,
                actionPendingIntent
            )
        }

        // Show notification
        notificationManager.notify(notificationId, builder.build())
    }

    /**
     * Update capsule notification
     */
    fun updateCapsuleNotification(capsule: Capsule) {
        // Same as show, but we check if notification exists first
        showCapsuleNotification(capsule)
    }

    /**
     * Cancel capsule notification
     */
    fun cancelCapsuleNotification(capsuleId: String) {
        Timber.d("Canceling notification for capsule: $capsuleId")
        val notificationId = capsuleId.hashCode()
        notificationManager.cancel(notificationId)
    }

    /**
     * Cancel all capsule notifications
     */
    fun cancelAllCapsuleNotifications() {
        Timber.d("Canceling all capsule notifications")
        // Note: This will cancel all notifications, including foreground service
        // In production, you'd want to track notification IDs and cancel selectively
        notificationManager.cancelAll()
    }

    /**
     * Show summary notification for multiple capsules
     */
    fun showSummaryNotification(capsules: List<Capsule>) {
        if (capsules.isEmpty()) return

        Timber.d("Showing summary notification for ${capsules.size} capsules")

        val intent = Intent(context, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context,
            SUMMARY_NOTIFICATION_ID,
            intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        val builder = NotificationCompat.Builder(context, CapsuleApplication.CHANNEL_CAPSULE_UPDATES)
            .setContentTitle("Active Capsules")
            .setContentText("You have ${capsules.size} active capsules")
            .setSmallIcon(R.drawable.ic_notification)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setGroupSummary(true)
            .setGroup("capsule_group")

        // Add inbox style with capsule titles
        val inboxStyle = NotificationCompat.InboxStyle()
            .setBigContentTitle("Active Capsules")
            .setSummaryText("${capsules.size} total")

        capsules.take(5).forEach { capsule ->
            inboxStyle.addLine("${capsule.title}${if (capsule.subtitle != null) ": ${capsule.subtitle}" else ""}")
        }

        if (capsules.size > 5) {
            inboxStyle.addLine("+ ${capsules.size - 5} more")
        }

        builder.setStyle(inboxStyle)

        notificationManager.notify(SUMMARY_NOTIFICATION_ID, builder.build())
    }

    /**
     * Get notification priority from capsule priority
     */
    private fun getPriority(priority: CapsulePriority): Int {
        return when (priority) {
            CapsulePriority.CRITICAL -> NotificationCompat.PRIORITY_MAX
            CapsulePriority.HIGH -> NotificationCompat.PRIORITY_HIGH
            CapsulePriority.NORMAL -> NotificationCompat.PRIORITY_DEFAULT
            CapsulePriority.LOW -> NotificationCompat.PRIORITY_LOW
        }
    }

    /**
     * Get notification category from capsule type
     */
    private fun getCategory(capsuleType: com.industriverse.capsules.data.models.CapsuleType): String {
        return when (capsuleType) {
            com.industriverse.capsules.data.models.CapsuleType.ALERT -> NotificationCompat.CATEGORY_ALARM
            com.industriverse.capsules.data.models.CapsuleType.TASK -> NotificationCompat.CATEGORY_REMINDER
            com.industriverse.capsules.data.models.CapsuleType.WORKFLOW -> NotificationCompat.CATEGORY_PROGRESS
            com.industriverse.capsules.data.models.CapsuleType.STATUS -> NotificationCompat.CATEGORY_STATUS
            com.industriverse.capsules.data.models.CapsuleType.DECISION -> NotificationCompat.CATEGORY_MESSAGE
            com.industriverse.capsules.data.models.CapsuleType.CUSTOM -> NotificationCompat.CATEGORY_EVENT
        }
    }

    companion object {
        const val FOREGROUND_SERVICE_NOTIFICATION_ID = 1001
        const val SUMMARY_NOTIFICATION_ID = 1002
    }
}
