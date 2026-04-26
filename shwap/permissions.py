import frappe


PUBLIC_VISIBILITIES = ("Public listing only", "Public searchable")


def _is_manager(user: str) -> bool:
    try:
        roles = frappe.get_roles(user)
    except TypeError:
        roles = frappe.get_roles(user=user)
    return "System Manager" in roles or "Inventory Manager" in roles


def inventory_item_query(user):
    if not user or user == "Guest":
        return "`tabInventory Item`.`visibility` in ('Public listing only', 'Public searchable')"
    if _is_manager(user):
        return None
    escaped_user = frappe.db.escape(user)
    return (
        f"(`tabInventory Item`.`owner_user` = {escaped_user} "
        f"or `tabInventory Item`.`current_holder` = {escaped_user} "
        "or `tabInventory Item`.`visibility` in ('Public listing only', 'Public searchable') "
        "or (`tabInventory Item`.`owner_group` is not null and exists ("
        "select 1 from `tabGroup Member` gm "
        f"where gm.user = {escaped_user} and gm.parent = `tabInventory Item`.`owner_group` and gm.status = 'Active'"
        ")))"
    )


def inventory_item_has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    if not user or user == "Guest":
        return doc.visibility in PUBLIC_VISIBILITIES and permission_type in (None, "read")

    if _is_manager(user):
        return True
    if doc.owner_user == user or doc.current_holder == user:
        return True
    if permission_type in (None, "read") and doc.visibility in PUBLIC_VISIBILITIES:
        return True

    if doc.owner_group and permission_type in (None, "read"):
        return bool(
            frappe.db.exists(
                "Group Member",
                {
                    "parent": doc.owner_group,
                    "user": user,
                    "status": "Active",
                },
            )
        )
    return False


def listing_query(user):
    if not user or user == "Guest":
        return "`tabListing`.`visibility_audience` = 'Public'"
    if _is_manager(user):
        return None
    escaped_user = frappe.db.escape(user)
    return (
        f"(`tabListing`.`owner` = {escaped_user} "
        "or `tabListing`.`visibility_audience` = 'Public' "
        "or (`tabListing`.`visibility_audience` in ('Household','Specific group','Trusted circles') and exists ("
        "select 1 from `tabInventory Item` it "
        "inner join `tabGroup Member` gm on gm.parent = it.owner_group "
        "where it.name = `tabListing`.`inventory_item` "
        f"and gm.user = {escaped_user} and gm.status = 'Active'"
        ")))"
    )


def listing_has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    if not user or user == "Guest":
        return doc.visibility_audience == "Public" and permission_type in (None, "read")

    if _is_manager(user):
        return True

    if doc.owner == user:
        return True

    if permission_type in (None, "read") and doc.visibility_audience == "Public":
        return True

    if permission_type in (None, "read") and doc.inventory_item:
        item = frappe.get_cached_doc("Inventory Item", doc.inventory_item)
        return inventory_item_has_permission(item, user=user, permission_type="read")

    return False
