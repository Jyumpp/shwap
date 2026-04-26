import frappe

from shwap.api import _portal_bootstrap_data


def get_portal_context(context, page_name: str, page_title: str):
    context.no_cache = 1
    context.show_sidebar = False
    context.page_name = page_name
    context.title = page_title

    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = f"/login?redirect-to=/{page_name}"
        raise frappe.Redirect

    context.initial_data = _portal_bootstrap_data(frappe.session.user)
    context.user_email = frappe.session.user
