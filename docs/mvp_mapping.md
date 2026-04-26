# shwap MVP Mapping (Design Doc → Frappe)

## Implemented DocTypes

### Core MVP

- `Inventory Item`
- `Item Category`
- `Location`
- `Listing`
- `Lending Transaction`
- `Shwap Group`
- `Wanted Request`
- `Clothing Detail`
- `Fit Profile`

### Support DocTypes for auditability

- `Inventory Movement`
- `Item Condition Log`
- `Group Member` (child table)

## Naming Series

- `Inventory Item`: `ITEM-.YYYY.-.#####`
- `Listing`: `LIST-.YYYY.-.#####`
- `Lending Transaction`: `LEND-.YYYY.-.#####`
- `Wanted Request`: `REQ-.YYYY.-.#####`

## Workflow/Hook Behavior Included

- Inventory update logs movements when holder/location changes.
- Inventory update creates condition logs when condition changes.
- Listing validation inherits default metadata from inventory item.
- Visibility permission rules are enforced for Inventory Item and Listing.
- Lending transaction update syncs inventory status:
  - `Checked out`/`Due soon`/`Overdue` → item `Lent out`
  - `Returned accepted`/`Closed` → item `Active`
  - `Returned damaged` → item `Needs repair`
  - `Lost` → item `Missing`

## API Endpoints

- `quick_add_item(payload)`
- `create_listing_from_item(item, listing_type, payload)`
- `start_lending_transaction(item, borrower, due_date, payload)`
- `search_inventory(query=None, status=None, location=None)`
- `dashboard_summary()`
- `lending_queue()`
- `estimate_fit_for_item(clothing_detail, fit_profile)`
- `portal_bootstrap()`
- `portal_quick_add_item(payload)`
- `portal_create_wanted_request(payload)`

## Public-Facing Route

- `/inventory` (login required) for non-Desk user view.

## MVP Feature Status

- ✅ Mobile-friendly quick add (`Inventory Item` quick entry + list quick-add button)
- ✅ Item photos (`primary_photo`)
- ✅ Categories and tags (`Item Category`, `Inventory Item.tags`)
- ✅ Locations (`Location` + linked on item)
- ✅ Private inventory defaults (`visibility` default = `Private`)
- ✅ Group inventory (`owner_group` + group-aware permissions)
- ✅ Listing generated from inventory item (API + form button)
- ✅ Lending workflow and lifecycle (`Lending Transaction` + workflow bootstrap)
- ✅ Basic trade/swap listing (`Listing.listing_type` includes `Trade` / `Swap`)
- ✅ Wanted requests (`Wanted Request`)
- ✅ Clothing measurements (`Clothing Detail`)
- ✅ Basic fit profile (`Fit Profile` + fit estimate)
- ✅ QR payload per item (`Inventory Item.qr_payload`)
- ✅ Search and filters (`search_fields` + list filters + `search_inventory`)
