package com.aerofinder.data

import android.content.Context
import android.content.SharedPreferences

class PreferencesManager(context: Context) {
    private val prefs: SharedPreferences =
        context.getSharedPreferences("aerofinder_prefs", Context.MODE_PRIVATE)

    var isAppNotificationEnabled: Boolean
        get() = prefs.getBoolean("app_notification_enabled", true)
        set(value) {
            prefs.edit().putBoolean("app_notification_enabled", value).apply()
        }

    fun isAirlineNotificationEnabled(airlineId: String): Boolean {
        return prefs.getBoolean("airline_$airlineId", true)
    }

    fun setAirlineNotificationEnabled(airlineId: String, enabled: Boolean) {
        prefs.edit().putBoolean("airline_$airlineId", enabled).apply()
    }
}
