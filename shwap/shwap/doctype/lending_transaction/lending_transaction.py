import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


LENDING_STATUSES = {
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
}


class LendingTransaction(Document):
    def validate(self):
        validate_lending_transaction(self, None)

    def on_update(self):
        on_update_lending_transaction(self, None)


def validate_lending_transaction(doc, _method):
    if doc.status and doc.status not in LENDING_STATUSES:
        frappe.throw(_("Invalid lending status: {0}").format(doc.status))

    if doc.due_date and doc.requested_start:
        if getdate(doc.due_date) < getdate(doc.requested_start):
            frappe.throw(_("Due Date cannot be before Requested Start."))


def on_update_lending_transaction(doc, _method):
    if not doc.inventory_item:
        return

    item = frappe.get_doc("Inventory Item", doc.inventory_item)

    if doc.status in {"Checked out", "Due soon", "Overdue"}:
        if item.status != "Lent out":
            item.status = "Lent out"
            item.current_holder = doc.borrower
            item.save(ignore_permissions=True)

    if doc.status in {"Returned accepted", "Closed"}:
        if item.status == "Lent out":
            item.status = "Active"
            item.current_holder = doc.lender
            item.save(ignore_permissions=True)

    if doc.status in {"Returned damaged"}:
        item.status = "Needs repair"
        item.current_holder = doc.lender
        item.save(ignore_permissions=True)

    if doc.status == "Lost":
        item.status = "Missing"
        item.current_holder = doc.borrower
        item.save(ignore_permissions=True)
