package com.aerofinder.data

import com.google.gson.annotations.SerializedName

/**
 * 백엔드 GET /api/airlines 응답 한 건
 */
data class Airline(
    val id: String,
    val name: String,
    @SerializedName("base_url") val baseUrl: String,
    @SerializedName("logo_url") val logoUrl: String? = null,
)
