import frappe
from frappe import _
from frappe.model.document import Document


class Listing(Document):
    def validate(self):
        validate_listing(self, None)


def validate_listing(doc, _method):
    item = frappe.get_doc("Inventory Item", doc.inventory_item)

    roles = frappe.get_roles()
    if item.owner_user and item.owner_user != frappe.session.user and "System Manager" not in roles and "Inventory Manager" not in roles:
        frappe.throw(_("Only the item owner can create/update listings."))

    if not doc.title:
        doc.title = item.item_name

    if not doc.description:
        doc.description = item.public_description or item.notes

    if not doc.location_area:
        doc.location_area = item.location

    if not doc.created_by_user:
        doc.created_by_user = frappe.session.user
