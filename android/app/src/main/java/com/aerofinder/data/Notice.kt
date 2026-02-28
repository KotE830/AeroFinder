package com.aerofinder.data

import com.google.gson.annotations.SerializedName

/**
 * 백엔드 GET /api/notices 응답 한 건 (크롤링된 전체 공지)
 */
data class Notice(
    val id: String,
    val airline: String,
    @SerializedName("source_url") val sourceUrl: String,
    val title: String,
    @SerializedName("content_type") val contentType: String,
    @SerializedName("event_start") val eventStart: String? = null,
    @SerializedName("event_end") val eventEnd: String? = null,
    @SerializedName("is_special_deal") val isSpecialDeal: Boolean = false,
    @SerializedName("created_at") val createdAt: String? = null,
)
