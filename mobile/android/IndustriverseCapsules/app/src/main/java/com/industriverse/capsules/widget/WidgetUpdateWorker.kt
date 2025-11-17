package com.industriverse.capsules.widget

import android.content.Context
import androidx.glance.appwidget.GlanceAppWidgetManager
import androidx.glance.appwidget.state.updateAppWidgetState
import androidx.glance.appwidget.updateAll
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import timber.log.Timber

/**
 * Widget Update Worker
 * Week 13 Day 5-6: Background worker for periodic widget updates
 *
 * This worker runs every 15 minutes to update all active widgets
 * with the latest capsule data from the local database.
 */
class WidgetUpdateWorker(
    private val context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            Timber.d("Widget update worker starting")

            // Update all widget types
            updateCompactWidgets()
            updateExpandedWidgets()
            updateFullWidgets()

            Timber.d("Widget update worker completed successfully")
            Result.success()
        } catch (e: Exception) {
            Timber.e(e, "Widget update worker failed")
            Result.retry()
        }
    }

    /**
     * Update all compact (1x1) widgets
     */
    private suspend fun updateCompactWidgets() {
        val glanceManager = GlanceAppWidgetManager(context)
        val glanceIds = glanceManager.getGlanceIds(CompactCapsuleWidget::class.java)

        glanceIds.forEach { glanceId ->
            updateAppWidgetState(context, glanceId) { prefs ->
                // Update widget state if needed
                // For now, the widget fetches data directly
            }
        }

        // Trigger widget refresh
        CompactCapsuleWidget().updateAll(context)
    }

    /**
     * Update all expanded (2x2) widgets
     */
    private suspend fun updateExpandedWidgets() {
        val glanceManager = GlanceAppWidgetManager(context)
        val glanceIds = glanceManager.getGlanceIds(ExpandedCapsuleWidget::class.java)

        glanceIds.forEach { glanceId ->
            updateAppWidgetState(context, glanceId) { prefs ->
                // Update widget state if needed
            }
        }

        // Trigger widget refresh
        ExpandedCapsuleWidget().updateAll(context)
    }

    /**
     * Update all full (4x2) widgets
     */
    private suspend fun updateFullWidgets() {
        val glanceManager = GlanceAppWidgetManager(context)
        val glanceIds = glanceManager.getGlanceIds(FullCapsuleWidget::class.java)

        glanceIds.forEach { glanceId ->
            updateAppWidgetState(context, glanceId) { prefs ->
                // Update widget state if needed
            }
        }

        // Trigger widget refresh
        FullCapsuleWidget().updateAll(context)
    }
}
