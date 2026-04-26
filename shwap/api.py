import json
from typing import Optional

import frappe
from frappe import _
from frappe.utils import getdate, nowdate
from shwap.utils.fit import evaluate_fit


def _parse_json(value):
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    return json.loads(value)


def _ensure_doc(doctype: str, name: str):
    if not frappe.db.exists(doctype, name):
        frappe.throw(_("{0} not found: {1}").format(doctype, name))
    return frappe.get_doc(doctype, name)


def _assert_doctype_permission(doctype: str, ptype: str):
    if not frappe.has_permission(doctype=doctype, ptype=ptype):
        frappe.throw(_("Not permitted to {0} {1}.").format(ptype, doctype), frappe.PermissionError)


def _assert_choice(value: str, allowed: set, label: str):
    if value not in allowed:
        frappe.throw(_("{0} must be one of: {1}").format(label, ", ".join(sorted(allowed))))


def _require_logged_in():
    if frappe.session.user == "Guest":
        frappe.throw(_("Please log in to continue."), frappe.PermissionError)


def _portal_bootstrap_data(user: str):
    summary = {
        "total_items": frappe.db.count(
            "Inventory Item",
            {"owner_user": user},
        ),
        "lent_out": frappe.db.count(
            "Inventory Item",
            {"owner_user": user, "status": "Lent out"},
        ),
        "active_listings": frappe.db.count(
            "Listing",
            {"owner": user, "listing_status": "Active"},
        ),
        "open_requests": frappe.db.count(
            "Wanted Request",
            {"requester": user, "status": "Open"},
        ),
    }

    items = frappe.get_all(
        "Inventory Item",
        filters={"owner_user": user},
        fields=[
            "name",
            "item_name",
            "category",
            "location",
            "status",
            "condition",
            "visibility",
            "primary_photo",
            "qr_payload",
            "modified",
        ],
        order_by="modified desc",
        limit_page_length=50,
    )

    listings = frappe.get_all(
        "Listing",
        filters={"owner": user},
        fields=[
            "name",
            "inventory_item",
            "listing_type",
            "listing_status",
            "title",
            "price",
            "modified",
        ],
        order_by="modified desc",
        limit_page_length=50,
    )

    lending = frappe.get_all(
        "Lending Transaction",
        or_filters={"lender": user, "borrower": user},
        fields=[
            "name",
            "inventory_item",
            "lender",
            "borrower",
            "status",
            "due_date",
            "return_date",
            "modified",
        ],
        order_by="modified desc",
        limit_page_length=50,
    )

    requests = frappe.get_all(
        "Wanted Request",
        filters={"requester": user},
        fields=[
            "name",
            "title",
            "request_type",
            "category",
            "needed_by",
            "budget",
            "status",
            "modified",
        ],
        order_by="modified desc",
        limit_page_length=50,
    )

    categories = frappe.get_all("Item Category", fields=["name"], order_by="name asc")
    locations = frappe.get_all("Location", fields=["name"], order_by="name asc")

    return {
        "summary": summary,
        "items": items,
        "listings": listings,
        "lending": lending,
        "requests": requests,
        "categories": [entry.name for entry in categories],
        "locations": [entry.name for entry in locations],
    }


@frappe.whitelist()
def quick_add_item(payload=None):
    _assert_doctype_permission("Inventory Item", "create")
    data = _parse_json(payload)
    required = ["item_name", "category", "location"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    doc = frappe.new_doc("Inventory Item")
    doc.item_name = data.get("item_name")
    doc.category = data.get("category")
    doc.location = data.get("location")
    doc.condition = data.get("condition") or "Good"
    doc.visibility = data.get("visibility") or "Private"
    doc.ownership_scope = data.get("ownership_scope") or "Private"
    doc.status = data.get("status") or "Active"
    doc.owner_user = data.get("owner_user") or frappe.session.user
    doc.current_holder = data.get("current_holder") or frappe.session.user
    doc.owner_group = data.get("owner_group")
    doc.brand = data.get("brand")
    doc.model = data.get("model")
    doc.serial_number = data.get("serial_number")
    doc.replacement_value = data.get("replacement_value") or 0
    doc.notes = data.get("notes")
    doc.insert()
    return {"name": doc.name, "qr_payload": doc.qr_payload}


@frappe.whitelist()
def create_listing_from_item(item: str, listing_type: str, payload=None):
    _assert_doctype_permission("Listing", "create")
    _assert_choice(listing_type, {"Sell", "Trade", "Swap", "Lend", "Gift", "Rent"}, "Listing Type")
    item_doc = _ensure_doc("Inventory Item", item)
    if not item_doc.has_permission("read"):
        frappe.throw(_("Not permitted to access Inventory Item {0}.").format(item_doc.name), frappe.PermissionError)

    data = _parse_json(payload)
    listing = frappe.new_doc("Listing")
    listing.inventory_item = item_doc.name
    listing.listing_type = listing_type
    listing_status = data.get("listing_status") or "Draft"
    _assert_choice(listing_status, {"Draft", "Active", "Paused", "Reserved", "Completed", "Cancelled", "Expired"}, "Listing Status")
    listing.listing_status = listing_status
    listing.title = data.get("title") or item_doc.item_name
    listing.description = data.get("description") or item_doc.public_description or item_doc.notes
    listing.visibility_audience = data.get("visibility_audience") or "Private"
    listing.price = data.get("price") or 0
    listing.trade_interests = data.get("trade_interests")
    listing.location_area = data.get("location_area") or item_doc.location
    listing.insert()
    if item_doc.status not in {"Listed", "Lent out"}:
        item_doc.status = "Listed"
        item_doc.save()
    return {"name": listing.name}


@frappe.whitelist()
def start_lending_transaction(item: str, borrower: str, due_date: str, payload=None):
    _assert_doctype_permission("Lending Transaction", "create")
    item_doc = _ensure_doc("Inventory Item", item)
    if not item_doc.has_permission("read"):
        frappe.throw(_("Not permitted to access Inventory Item {0}.").format(item_doc.name), frappe.PermissionError)

    data = _parse_json(payload)
    if getdate(due_date) < getdate(nowdate()):
        frappe.throw(_("Due Date cannot be in the past."))

    transaction = frappe.new_doc("Lending Transaction")
    transaction.inventory_item = item_doc.name
    transaction.lender = data.get("lender") or frappe.session.user
    transaction.borrower = borrower
    status = data.get("status") or "Requested"
    _assert_choice(
        status,
        {
            "Available",
            "Requested",
            "Approved",
            "Scheduled for pickup",
            "Checked out",
            "Due soon",
            "Overdue",
            "Returned pending inspection",
            "Returned accepted",
            "Returned damaged",
            "Lost",
            "Dispute opened",
            "Closed",
        },
        "Lending Status",
    )
    transaction.status = status
    transaction.requested_start = data.get("requested_start") or nowdate()
    transaction.due_date = due_date
    transaction.deposit_amount = data.get("deposit_amount") or 0
    transaction.pickup_location = data.get("pickup_location")
    transaction.return_location = data.get("return_location")
    transaction.pre_lend_condition = data.get("pre_lend_condition")
    transaction.notes = data.get("notes")
    transaction.insert()
    return {"name": transaction.name}


@frappe.whitelist()
def search_inventory(query: Optional[str] = None, status: Optional[str] = None, location: Optional[str] = None):
    filters = {}
    if status:
        filters["status"] = status
    if location:
        filters["location"] = location

    or_filters = []
    if query:
        wildcard = f"%{query}%"
        for fieldname in ["item_name", "brand", "model", "serial_number", "notes", "public_description", "tags"]:
            or_filters.append([fieldname, "like", wildcard])

    docs = frappe.get_all(
        "Inventory Item",
        filters=filters,
        or_filters=or_filters if or_filters else None,
        fields=[
            "name",
            "item_name",
            "category",
            "location",
            "status",
            "condition",
            "visibility",
            "current_holder",
        ],
        order_by="modified desc",
    )
    return docs


@frappe.whitelist()
def dashboard_summary():
    statuses = ["Active", "Lent out", "Listed", "Needs repair", "Missing"]
    response = {
        "total_items": frappe.db.count("Inventory Item"),
        "active_listings": frappe.db.count("Listing", {"listing_status": "Active"}),
        "open_requests": frappe.db.count("Wanted Request", {"status": "Open"}),
        "due_today": frappe.db.count("Lending Transaction", {"due_date": nowdate(), "status": ["not in", ["Closed", "Returned accepted"]]}),
    }
    for status in statuses:
        key = status.lower().replace(" ", "_")
        response[key] = frappe.db.count("Inventory Item", {"status": status})
    return response


@frappe.whitelist()
def lending_queue():
    return {
        "pending_requests": frappe.get_all(
            "Lending Transaction",
            filters={"status": "Requested"},
            fields=["name", "inventory_item", "lender", "borrower", "due_date", "requested_start"],
            order_by="creation desc",
        ),
        "due_soon": frappe.get_all(
            "Lending Transaction",
            filters={"status": ["in", ["Checked out", "Due soon", "Overdue"]]},
            fields=["name", "inventory_item", "lender", "borrower", "due_date", "status"],
            order_by="due_date asc",
        ),
    }


@frappe.whitelist()
def portal_bootstrap():
    _require_logged_in()
    return _portal_bootstrap_data(frappe.session.user)


@frappe.whitelist()
def portal_quick_add_item(payload=None):
    _require_logged_in()
    data = _parse_json(payload)
    return quick_add_item(
        payload={
            "item_name": data.get("item_name"),
            "category": data.get("category"),
            "location": data.get("location"),
            "condition": data.get("condition") or "Good",
            "visibility": data.get("visibility") or "Private",
            "status": "Active",
            "owner_user": frappe.session.user,
            "current_holder": frappe.session.user,
            "notes": data.get("notes"),
        }
    )


@frappe.whitelist()
def portal_create_wanted_request(payload=None):
    _require_logged_in()
    _assert_doctype_permission("Wanted Request", "create")
    data = _parse_json(payload)
    if not data.get("title") or not data.get("request_type"):
        frappe.throw(_("Title and Request Type are required."))

    request = frappe.new_doc("Wanted Request")
    request.requester = frappe.session.user
    request.title = data.get("title")
    request.request_type = data.get("request_type")
    request.category = data.get("category")
    request.description = data.get("description")
    request.desired_condition = data.get("desired_condition") or "Any"
    request.budget = data.get("budget") or 0
    request.needed_by = data.get("needed_by")
    request.location_radius = data.get("location_radius")
    request.visibility_audience = data.get("visibility_audience") or "Private"
    request.status = "Open"
    request.insert()
    return {"name": request.name}


@frappe.whitelist()
def estimate_fit_for_item(clothing_detail: str, fit_profile: str):
    detail = _ensure_doc("Clothing Detail", clothing_detail)
    profile = _ensure_doc("Fit Profile", fit_profile)
    return evaluate_fit(
        {
            "chest_bust": detail.chest_bust,
            "waist": detail.waist,
            "hip": detail.hip,
            "inseam": detail.inseam,
        },
        {
            "chest_bust": profile.chest_bust,
            "waist": profile.waist,
            "hip": profile.hip,
            "inseam": profile.inseam,
        },
    )
