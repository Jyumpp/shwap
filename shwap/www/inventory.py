from shwap.portal import get_portal_context


def get_context(context):
    get_portal_context(context, page_name="inventory", page_title="Shwap Dashboard")
