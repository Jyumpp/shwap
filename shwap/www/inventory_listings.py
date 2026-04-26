from shwap.portal import get_portal_context


def get_context(context):
    get_portal_context(context, page_name="inventory-listings", page_title="Listings")
