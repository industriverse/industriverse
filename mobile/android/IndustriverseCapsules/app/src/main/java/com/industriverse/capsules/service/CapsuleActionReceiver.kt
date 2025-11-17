package com.industriverse.capsules.service

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import timber.log.Timber

/**
 * Broadcast Receiver for handling capsule action button clicks from notifications
 * Week 13: Android Native Implementation
 */
class CapsuleActionReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val capsuleId = intent.getStringExtra("capsule_id")
        val actionId = intent.getStringExtra("action_id")

        if (capsuleId == null || actionId == null) {
            Timber.w("Received action intent without capsule_id or action_id")
            return
        }

        Timber.d("Action button clicked: capsuleId=$capsuleId, actionId=$actionId")

        // Forward to CapsuleService for execution
        val serviceIntent = Intent(context, CapsuleService::class.java).apply {
            action = CapsuleService.ACTION_EXECUTE_ACTION
            putExtra(CapsuleService.EXTRA_CAPSULE_ID, capsuleId)
            putExtra(CapsuleService.EXTRA_ACTION_ID, actionId)
        }

        context.startService(serviceIntent)
    }
}
