package com.aerofinder.data

import com.google.gson.annotations.SerializedName

/**
 * 백엔드 GET /api/deals 응답 한 건
 */
data class Deal(
    val id: String,
    val airline: String,
    @SerializedName("airline_id") val airlineId: String,
    val title: String,
    val description: String? = null,
    val url: String,
    @SerializedName("image_url") val imageUrl: String? = null,
    @SerializedName("event_start") val eventStart: String? = null,
    @SerializedName("event_end") val eventEnd: String? = null,
    val routes: Any? = null,
    val price: Number? = null,
    @SerializedName("created_at") val createdAt: String? = null,
)
