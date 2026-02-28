package com.aerofinder.worker

import android.app.PendingIntent
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.aerofinder.data.DealsRepository
import com.aerofinder.data.PreferencesManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

private const val CHANNEL_ID = "aerofinder_deals"
private const val PREFS_NAME = "aerofinder_deals"
private const val KEY_KNOWN_IDS = "known_deal_ids"

class DealsCheckWorker(
    context: Context,
    params: WorkerParameters,
) : CoroutineWorker(context, params) {

    private val repo = DealsRepository()
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            val result = repo.getDeals()
            val list = result.getOrElse { return@withContext Result.failure() }
            val currentIds = list.map { it.id }.toSet()
            val knownIds = prefs.getStringSet(KEY_KNOWN_IDS, emptySet()) ?: emptySet()
            val newIds = currentIds - knownIds

            if (newIds.isNotEmpty()) {
                val newDeals = list.filter { it.id in newIds }
                
                val prefsManager = PreferencesManager(applicationContext)
                
                newDeals.forEach { deal ->
                    if (prefsManager.isAppNotificationEnabled && 
                        prefsManager.isAirlineNotificationEnabled(deal.airlineId)) {
                        showNotification(deal.airline, deal.title, deal.url)
                    }
                }
                prefs.edit().putStringSet(KEY_KNOWN_IDS, currentIds).apply()
            } else if (knownIds.isEmpty() && list.isNotEmpty()) {
                prefs.edit().putStringSet(KEY_KNOWN_IDS, currentIds).apply()
            }
            Result.success()
        } catch (e: Exception) {
            Result.failure()
        }
    }

    @android.annotation.SuppressLint("MissingPermission")
    private fun showNotification(airline: String, title: String, url: String) {
        createChannel()
        val openIntent = Intent(Intent.ACTION_VIEW, Uri.parse(url)).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        val pending = PendingIntent.getActivity(
            applicationContext,
            url.hashCode(),
            openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("$airline 특가")
            .setContentText(title)
            .setContentIntent(pending)
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()
        NotificationManagerCompat.from(applicationContext).notify(url.hashCode(), notification)
    }

    private fun createChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(CHANNEL_ID, "특가 알림", NotificationManager.IMPORTANCE_DEFAULT)
            (applicationContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager)
                .createNotificationChannel(channel)
        }
    }
}
