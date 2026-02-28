package com.aerofinder

import android.app.Application
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.aerofinder.worker.DealsCheckWorker
import com.google.firebase.messaging.FirebaseMessaging
import java.util.concurrent.TimeUnit

class AeroFinderApp : Application() {

    override fun onCreate() {
        super.onCreate()
        scheduleDealsCheck()

        // Subscribe to FCM topic for global push notifications
        FirebaseMessaging.getInstance().subscribeToTopic("all_users")
    }

    private fun scheduleDealsCheck() {
        val request = PeriodicWorkRequestBuilder<DealsCheckWorker>(15, TimeUnit.MINUTES)
            .build()
        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "deals_check",
            ExistingPeriodicWorkPolicy.KEEP,
            request,
        )
    }
}
