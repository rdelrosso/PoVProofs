package com.mongodb.listings.model

import io.realm.RealmObject
import io.realm.RealmList
import io.realm.annotations.PrimaryKey
import io.realm.annotations.RealmClass
//import io.realm.annotations.Required
import org.bson.types.ObjectId
import java.util.Date

@RealmClass(embedded = true)
open class Listing_bookingRequests (    var bookedAt: Date? = null,
                               var confirmedAt: Date? = null,
                               var booked: Boolean? = false,
                               var confirmed: Boolean? = false,
                               var bookedByUserId: String? = null
) : RealmObject() {

}

open class Listing(
    var name: String = "My listing",
    var property_type: String = "Resort",
    var bookingRequests: RealmList<Listing_bookingRequests>? = null
) : RealmObject() {
    @PrimaryKey
    var _id: String = ObjectId().toString()
}