import frappe
from frappe.exceptions import LinkValidationError


ROLES = [
    "Shwap User",
    "Group Member",
    "Group Manager",
    "Inventory Manager",
    "Moderator",
]


def after_install():
    create_roles()
    seed_default_categories()
    seed_default_locations()
    create_workspace()
    create_lending_workflow()


def create_roles():
    for role_name in ROLES:
        if frappe.db.exists("Role", role_name):
            continue
        role = frappe.new_doc("Role")
        role.role_name = role_name
        role.desk_access = 1
        role.insert(ignore_permissions=True)


def seed_default_categories():
    categories = {
        "Tools": ["Power tools", "Hand tools", "Yard tools"],
        "Leisure": ["Sports equipment", "Camping gear", "Gaming consoles", "Board games"],
        "Clothing": ["Tops", "Bottoms", "Shoes", "Outerwear", "Accessories"],
        "Electronics": [],
        "Household": [],
        "Books/media": [],
    }

    for parent_name, children in categories.items():
        parent = _ensure_category(parent_name)
        for child_name in children:
            _ensure_category(child_name, parent.name)


def _ensure_category(category_name: str, parent: str = None):
    existing = frappe.db.exists("Item Category", category_name)
    if existing:
        return frappe.get_doc("Item Category", existing)

    doc = frappe.new_doc("Item Category")
    doc.category_name = category_name
    doc.parent_category = parent
    doc.insert(ignore_permissions=True)
    return doc


def seed_default_locations():
    locations = ["Home", "Garage", "Closet", "Storage Bin"]
    for location_name in locations:
        if frappe.db.exists("Location", location_name):
            continue
        doc = frappe.new_doc("Location")
        doc.location_name = location_name
        doc.location_type = location_name if location_name in {"Garage", "Closet", "Storage Bin"} else "House"
        doc.privacy_level = "Exact private"
        doc.insert(ignore_permissions=True)


def create_workspace():
    if frappe.db.exists("Workspace", "Shwap"):
        return

    content = [
        {
            "id": "header-main",
            "type": "header",
            "data": {"text": "Inventory"},
        },
        {
            "id": "shortcut-inventory",
            "type": "shortcut",
            "data": {
                "shortcut_name": "Inventory Item",
                "col": 3,
                "type": "DocType",
                "link_to": "Inventory Item",
            },
        },
        {
            "id": "shortcut-listing",
            "type": "shortcut",
            "data": {
                "shortcut_name": "Listing",
                "col": 3,
                "type": "DocType",
                "link_to": "Listing",
            },
        },
        {
            "id": "shortcut-lending",
            "type": "shortcut",
            "data": {
                "shortcut_name": "Lending Transaction",
                "col": 3,
                "type": "DocType",
                "link_to": "Lending Transaction",
            },
        },
        {
            "id": "shortcut-requests",
            "type": "shortcut",
            "data": {
                "shortcut_name": "Wanted Request",
                "col": 3,
                "type": "DocType",
                "link_to": "Wanted Request",
            },
        },
        {
            "id": "header-config",
            "type": "header",
            "data": {"text": "Setup"},
        },
        {
            "id": "shortcut-categories",
            "type": "shortcut",
            "data": {
                "shortcut_name": "Item Category",
                "col": 4,
                "type": "DocType",
                "link_to": "Item Category",
            },
        },
        {
            "id": "shortcut-locations",
            "type": "shortcut",
            "data": {
                "shortcut_name": "Location",
                "col": 4,
                "type": "DocType",
                "link_to": "Location",
            },
        },
        {
            "id": "shortcut-groups",
            "type": "shortcut",
            "data": {
                "shortcut_name": "Shwap Group",
                "col": 4,
                "type": "DocType",
                "link_to": "Shwap Group",
            },
        },
    ]

    workspace = frappe.new_doc("Workspace")
    workspace.title = "Shwap"
    workspace.module = "Shwap"
    workspace.icon = "package"
    workspace.public = 1
    workspace.content = frappe.as_json(content)
    workspace.label = "Shwap"
    workspace.insert(ignore_permissions=True)


def create_lending_workflow():
    workflow_name = "Lending Transaction Workflow"
    if frappe.db.exists("Workflow", workflow_name):
        return

    states = [
        ("Requested", "Shwap User", 0),
        ("Approved", "Inventory Manager", 0),
        ("Checked out", "Inventory Manager", 0),
        ("Returned accepted", "Inventory Manager", 0),
        ("Closed", "Inventory Manager", 1),
    ]
    actions = ["Approve", "Checkout", "Mark Returned", "Close"]

    try:
        _ensure_workflow_states([state_name for state_name, _, _ in states])
        _ensure_workflow_actions(actions)

        workflow = frappe.new_doc("Workflow")
        workflow.workflow_name = workflow_name
        workflow.document_type = "Lending Transaction"
        workflow.is_active = 1
        workflow.workflow_state_field = "status"

        for state_name, role, doc_status in states:
            workflow.append(
                "states",
                {
                    "state": state_name,
                    "allow_edit": role,
                    "doc_status": doc_status,
                },
            )

        for source, action, target, role in [
            ("Requested", "Approve", "Approved", "Inventory Manager"),
            ("Approved", "Checkout", "Checked out", "Inventory Manager"),
            ("Checked out", "Mark Returned", "Returned accepted", "Inventory Manager"),
            ("Returned accepted", "Close", "Closed", "Inventory Manager"),
        ]:
            workflow.append(
                "transitions",
                {
                    "state": source,
                    "action": action,
                    "next_state": target,
                    "allowed": role,
                },
            )

        workflow.insert(ignore_permissions=True)
    except LinkValidationError:
        frappe.log_error(
            title="Shwap Workflow Setup Skipped",
            message="Unable to create Lending Transaction workflow due to missing linked workflow metadata. "
            "App installation continues; create workflow manually if needed.",
        )


def _ensure_workflow_states(state_names: list[str]):
    if not frappe.db.exists("DocType", "Workflow State"):
        return

    for state_name in state_names:
        if frappe.db.exists("Workflow State", state_name):
            continue
        state = frappe.new_doc("Workflow State")
        state.workflow_state_name = state_name
        state.style = "Primary"
        state.insert(ignore_permissions=True)


def _ensure_workflow_actions(action_names: list[str]):
    action_doctype = "Workflow Action Master"
    if not frappe.db.exists("DocType", action_doctype):
        return

    for action_name in action_names:
        if frappe.db.exists(action_doctype, action_name):
            continue
        action = frappe.new_doc(action_doctype)
        action.workflow_action_name = action_name
        action.insert(ignore_permissions=True)
