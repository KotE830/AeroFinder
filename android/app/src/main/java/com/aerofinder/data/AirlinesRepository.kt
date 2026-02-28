package com.aerofinder.data

import com.aerofinder.BuildConfig
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

class AirlinesRepository {

    private val api: AeroFinderApi by lazy {
        val client = OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .build()
        Retrofit.Builder()
            .baseUrl(ensureTrailingSlash(BuildConfig.API_BASE_URL))
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(AeroFinderApi::class.java)
    }

    suspend fun getAirlines(): Result<List<Airline>> = withContext(Dispatchers.IO) {
        try {
            Result.success(api.getAirlines())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun ensureTrailingSlash(url: String): String =
        if (url.endsWith("/")) url else "$url/"
}
