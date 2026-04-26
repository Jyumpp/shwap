app_name = "shwap"
app_title = "shwap"
app_publisher = "shwap.trade"
app_description = "Inventory-first lending and exchange app"
app_email = "hello@shwap.trade"
app_license = "MIT"

required_apps = []
after_install = "shwap.install.after_install"
after_migrate = "shwap.install.after_install"

doctype_js = {
    "Inventory Item": "public/js/inventory_item.js",
    "Listing": "public/js/listing.js",
    "Lending Transaction": "public/js/lending_transaction.js",
}

doctype_list_js = {
    "Inventory Item": "public/js/inventory_item_list.js",
}

doc_events = {
    "Inventory Item": {
        "validate": "shwap.shwap.doctype.inventory_item.inventory_item.validate_inventory_item",
        "on_update": "shwap.shwap.doctype.inventory_item.inventory_item.on_update_inventory_item",
    },
    "Listing": {
        "validate": "shwap.shwap.doctype.listing.listing.validate_listing",
    },
    "Lending Transaction": {
        "validate": "shwap.shwap.doctype.lending_transaction.lending_transaction.validate_lending_transaction",
        "on_update": "shwap.shwap.doctype.lending_transaction.lending_transaction.on_update_lending_transaction",
    },
}

override_whitelisted_methods = {}

permission_query_conditions = {
    "Inventory Item": "shwap.permissions.inventory_item_query",
    "Listing": "shwap.permissions.listing_query",
}

has_permission = {
    "Inventory Item": "shwap.permissions.inventory_item_has_permission",
    "Listing": "shwap.permissions.listing_has_permission",
}

website_route_rules = [
    {"from_route": "/inventory-items", "to_route": "inventory_items"},
    {"from_route": "/inventory-listings", "to_route": "inventory_listings"},
    {"from_route": "/inventory-lending", "to_route": "inventory_lending"},
    {"from_route": "/inventory-requests", "to_route": "inventory_requests"},
    {"from_route": "/inventory-wardrobe", "to_route": "inventory_wardrobe"},
]
