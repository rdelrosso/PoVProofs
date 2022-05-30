package com.mongodb.listings.model

import androidx.appcompat.app.AlertDialog;
import android.util.Log
import android.view.*
import android.widget.Button
import android.widget.PopupMenu
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.card.MaterialCardView
import com.mongodb.listings.R
import com.mongodb.listings.TAG
import com.mongodb.listings.model.Listing_bookingRequests
import io.realm.OrderedRealmCollection
import io.realm.Realm
import io.realm.RealmRecyclerViewAdapter
import io.realm.kotlin.syncSession
import io.realm.kotlin.where
import java.text.DateFormat
import java.util.*


/*
 * ListAdapter: extends the Realm-provided RealmRecyclerViewAdapter to provide data for a RecyclerView to display
 * Realm objects on screen to a user.
 */
internal class ListingAdapter(data: OrderedRealmCollection<Listing>) :
    RealmRecyclerViewAdapter<Listing, ListingAdapter.ListingViewHolder?>(data, true) {
    private lateinit var _parent: ViewGroup
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ListingViewHolder {
        val itemView: View =
            LayoutInflater.from(parent.context).inflate(R.layout.listing_view, parent, false)
        _parent = parent
        return ListingViewHolder(itemView)
    }

    override fun onBindViewHolder(holder: ListingViewHolder, position: Int) {
        val obj: Listing? = getItem(position)
        val bgRealm = Realm.getDefaultInstance()

        // By default the listings are available to book
        var available = true
        var bookingRequestIndex = 0
        var bookedForUser = false
        var confirmedForUser = false
        holder.notAvailable.text = ""
        holder.notAvailable.visibility = View.GONE

        holder.bookedAt.text = ""
        holder.bookedAt.visibility = View.GONE

        holder.confirmedAt.text = ""
        holder.confirmedAt.visibility = View.GONE

        holder.bookButton.visibility = View.VISIBLE
        holder.cancelButton.visibility = View.INVISIBLE

        holder.card.setBackgroundColor(_parent.context.getColor(R.color.available))

        holder.data = obj
        holder.name.text = obj?.name


        for ((index, bookingRequest) in obj?.bookingRequests?.withIndex()!!) {
            // If the listing has a booking with a different user id, then it is not available
            if (bookingRequest.confirmed!! && bookingRequest.bookedByUserId != bgRealm.syncSession.user.id) {
                available = false
            }
            // Check if the listing has a booking by the current user
            if (bookingRequest.confirmed!! && bookingRequest.bookedByUserId == bgRealm.syncSession.user.id) {
                bookingRequestIndex = index
                confirmedForUser = true
            }
            // Check if the listing has a confirmation for the current user
            if (bookingRequest.booked!! && bookingRequest.bookedByUserId == bgRealm.syncSession.user.id) {
                bookingRequestIndex = index
                bookedForUser = true
            }
        }

        // If the listing is not available, mark it as such
        if (!available) {
            holder.notAvailable.text = "Not Available"
            holder.notAvailable.visibility = View.VISIBLE

            holder.cancelButton.visibility = View.GONE
            holder.bookButton.visibility = View.GONE
            holder.itemView.isClickable = false

            holder.card.setBackgroundColor(_parent.context.getColor(R.color.notAvailable))
        } else { // The listing is available

            // If it is booked by the current user, mark it as such
            if (bookedForUser &&  obj?.bookingRequests?.get(bookingRequestIndex)?.bookedAt != null) {
                holder.bookedAt.text =
                    "Booked at: " + DateFormat.getDateTimeInstance().format(obj.bookingRequests?.get(bookingRequestIndex)?.bookedAt)
                holder.bookedAt.visibility = View.VISIBLE
                holder.cancelButton.visibility = View.VISIBLE
                holder.bookButton.visibility = View.GONE
                holder.card.setBackgroundColor(_parent.context.getColor(R.color.booked))
            }

            // If it has been confirmed, mark it as such
            if (confirmedForUser &&  obj?.bookingRequests?.get(bookingRequestIndex)?.confirmedAt != null) {
                holder.confirmedAt.text =
                    "Confirmed at: " + DateFormat.getDateTimeInstance().format(obj.bookingRequests?.get(bookingRequestIndex)?.confirmedAt)
                holder.confirmedAt.visibility = View.VISIBLE
                holder.cancelButton.visibility = View.VISIBLE
                holder.bookButton.visibility = View.GONE
                holder.card.setBackgroundColor(_parent.context.getColor(R.color.confirmed))
            }

            // Configure the book stay button
            holder.bookButton.setOnClickListener {
                val builder =
                    AlertDialog.Builder(_parent.context)
                builder.setTitle("Confirm booking")
                builder.setMessage("Please confirm if you want to proceed with your stay?")
                builder.setCancelable(false)
                builder.setPositiveButton("Confirm") { dialog, _ ->
                    run {
                        dialog.dismiss()
                        createBooking(holder.data?._id)
                    }
                }
                builder.setNegativeButton("Cancel") { dialog, _ ->
                    dialog.cancel()
                }
                builder.show()
            }

            // Configure the cancel stay button
            holder.cancelButton.setOnClickListener {
                val builder =
                    AlertDialog.Builder(_parent.context)
                builder.setTitle("Cancel booking")
                builder.setMessage("Please confirm if you want to proceed with the cancellation?")
                builder.setCancelable(false)
                builder.setPositiveButton("Confirm") { dialog, _ ->
                    run {
                        dialog.dismiss()
                        cancelBooking(holder, holder.data?._id)
                    }
                }
                builder.setNegativeButton("Cancel") { dialog, _ ->
                    dialog.cancel()
                }
                builder.show()
            }
        }
    }

    // Book a stay
    private fun createBooking(_id: String?) {
        // need to create a separate instance of realm to issue an update, since this event is
        // handled by a background thread and realm instances cannot be shared across threads
        val bgRealm = Realm.getDefaultInstance()
        // execute Transaction (not async) because changeStatus should execute on a background thread
        bgRealm!!.executeTransaction {
            // using our thread-local new realm instance, query for and update the booking status
            val item = it.where<Listing>().equalTo("_id", _id).findFirst()

            val bookingRequest = Listing_bookingRequests()
            bookingRequest.booked = true
            bookingRequest.bookedAt = Date()
            bookingRequest.bookedByUserId = bgRealm.syncSession.user.id

            item?.bookingRequests?.add(bookingRequest)
        }
        // always close realms when you are done with them!
        bgRealm.close()
    }

    // Cancel a stay
    private fun cancelBooking(holder: ListingViewHolder, _id: String?) {
        // need to create a separate instance of realm to issue an update, since this event is
        // handled by a background thread and realm instances cannot be shared across threads
        val bgRealm = Realm.getDefaultInstance()
        // execute Transaction (not async) because changeStatus should execute on a background thread
        bgRealm!!.executeTransaction {
            // using our thread-local new realm instance, query for and update the booking status
            val item = it.where<Listing>().equalTo("_id", _id).findFirst()
            item?.bookingRequests = null

            holder.bookedAt.text = ""
            holder.confirmedAt.text = ""
        }
        // always close realms when you are done with them!
        bgRealm.close()
    }

    internal inner class ListingViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        var name: TextView = view.findViewById(R.id.name)
        var bookedAt: TextView = view.findViewById(R.id.bookedAt)
        var confirmedAt: TextView = view.findViewById(R.id.confirmedAt)
        var data: Listing? = null

        var bookButton: Button = view.findViewById(R.id.bookButton)
        var cancelButton: Button = view.findViewById(R.id.cancelButton)
        var notAvailable: TextView = view.findViewById(R.id.notAvailable)
        var card: MaterialCardView = view.findViewById(R.id.card)
    }
}
