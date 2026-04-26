import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url, now_datetime, nowdate


ALLOWED_STATUSES = {
    "Active",
    "Lent out",
    "Listed",
    "Reserved",
    "Missing",
    "Needs repair",
    "Archived",
    "Disposed",
}


class InventoryItem(Document):
    def validate(self):
        validate_inventory_item(self, None)

    def on_update(self):
        on_update_inventory_item(self, None)


def validate_inventory_item(doc, _method):
    if doc.status and doc.status not in ALLOWED_STATUSES:
        frappe.throw(_("Invalid inventory status: {0}").format(doc.status))

    if not doc.owner_user:
        doc.owner_user = frappe.session.user

    if not doc.current_holder:
        doc.current_holder = doc.owner_user

    if not doc.qr_payload:
        doc.qr_payload = _build_qr_payload(doc.name)

    if not doc.last_verified_date:
        doc.last_verified_date = nowdate()


def on_update_inventory_item(doc, _method):
    _log_movement_if_needed(doc)
    _log_condition_if_needed(doc)


def _build_qr_payload(item_name: str) -> str:
    base = get_url().rstrip("/")
    return f"{base}/app/inventory-item/{item_name}"


def _log_movement_if_needed(doc):
    if doc.is_new():
        return

    old = doc.get_doc_before_save()
    if not old:
        return

    location_changed = (old.location or "") != (doc.location or "")
    holder_changed = (old.current_holder or "") != (doc.current_holder or "")
    if not location_changed and not holder_changed:
        return

    movement = frappe.new_doc("Inventory Movement")
    movement.inventory_item = doc.name
    movement.from_location = old.location
    movement.to_location = doc.location
    movement.from_holder = old.current_holder
    movement.to_holder = doc.current_holder
    movement.movement_reason = "Inventory item update"
    movement.performed_by = frappe.session.user
    movement.timestamp = now_datetime()
    movement.insert(ignore_permissions=True)


def _log_condition_if_needed(doc):
    if doc.is_new():
        return

    old = doc.get_doc_before_save()
    if not old or (old.condition or "") == (doc.condition or ""):
        return

    log = frappe.new_doc("Item Condition Log")
    log.inventory_item = doc.name
    log.condition_rating = doc.condition
    log.condition_notes = doc.internal_notes or doc.notes
    log.logged_by = frappe.session.user
    log.logged_on = now_datetime()
    log.insert(ignore_permissions=True)
