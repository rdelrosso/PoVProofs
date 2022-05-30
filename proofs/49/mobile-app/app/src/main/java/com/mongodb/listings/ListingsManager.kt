package com.mongodb.listings

import android.app.Application

import io.realm.Realm
import io.realm.log.LogLevel
import io.realm.log.RealmLog
import io.realm.mongodb.App
import io.realm.mongodb.AppConfiguration

lateinit var listingsApp: App

// global Kotlin extension that resolves to the short version
// of the name of the current class. Used for labelling logs.
inline fun <reified T> T.TAG(): String = T::class.java.simpleName

/*
 * ListingsManager: Sets up the listingApp Realm App and enables Realm-specific logging in debug mode.
 */
class ListingsManager : Application() {

    override fun onCreate() {
        super.onCreate()
        Realm.init(this)
        listingsApp = App(AppConfiguration.Builder(BuildConfig.MONGODB_REALM_APP_ID)
            .baseUrl(BuildConfig.MONGODB_REALM_URL)
            .appName(BuildConfig.VERSION_NAME)
            .appVersion(BuildConfig.VERSION_CODE.toString())
            .build())

        // Enable more logging in debug mode
        if (BuildConfig.DEBUG) {
            RealmLog.setLevel(LogLevel.ALL)
        }
    }
}
