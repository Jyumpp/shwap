import frappe

from shwap.api import _portal_bootstrap_data


def get_context(context):
    context.no_cache = 1
    context.show_sidebar = False
    context.title = "Shwap Inventory"

    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/inventory"
        raise frappe.Redirect

    context.initial_data = _portal_bootstrap_data(frappe.session.user)
