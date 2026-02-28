package com.aerofinder.data

import retrofit2.http.GET
import retrofit2.http.Query

interface AeroFinderApi {
    @GET("api/deals")
    suspend fun getDeals(): List<Deal>

    @GET("api/airlines")
    suspend fun getAirlines(): List<Airline>

    @GET("api/notices")
    suspend fun getNotices(
        @Query("airline_id") airlineId: String? = null,
        @Query("is_special_deal") isSpecialDeal: Boolean? = null,
    ): List<Notice>
}
