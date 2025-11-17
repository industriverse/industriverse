package com.industriverse.capsules.widget

import android.content.Context
import androidx.glance.appwidget.GlanceAppWidget
import androidx.glance.appwidget.GlanceAppWidgetReceiver
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import java.util.concurrent.TimeUnit

/**
 * Compact Widget Provider (1x1)
 * Week 13 Day 5-6: Widget provider for compact home screen widget
 *
 * This provider manages the lifecycle of the compact (1x1) widget.
 * Shows the single highest priority capsule as a pill.
 */
class CompactWidgetProvider : GlanceAppWidgetReceiver() {

    override val glanceAppWidget: GlanceAppWidget = CompactCapsuleWidget()

    override fun onEnabled(context: Context) {
        super.onEnabled(context)

        // Schedule periodic widget updates every 15 minutes
        scheduleWidgetUpdates(context)
    }

    override fun onDisabled(context: Context) {
        super.onDisabled(context)

        // Cancel scheduled updates when last widget is removed
        cancelWidgetUpdates(context)
    }

    /**
     * Schedule periodic widget updates
     * Updates every 15 minutes to keep widget in sync with active capsules
     */
    private fun scheduleWidgetUpdates(context: Context) {
        val workRequest = PeriodicWorkRequestBuilder<WidgetUpdateWorker>(
            15, TimeUnit.MINUTES
        ).build()

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            WIDGET_UPDATE_WORK_NAME,
            ExistingPeriodicWorkPolicy.KEEP,
            workRequest
        )
    }

    /**
     * Cancel widget updates
     */
    private fun cancelWidgetUpdates(context: Context) {
        WorkManager.getInstance(context).cancelUniqueWork(WIDGET_UPDATE_WORK_NAME)
    }

    companion object {
        private const val WIDGET_UPDATE_WORK_NAME = "compact_widget_updates"
    }
}
