# shwap (Frappe App)

`shwap` is a Frappe app for inventory-first lending/trade workflows based on the provided design document.

## MVP Implemented

- Inventory-first data model (`Inventory Item` as source of truth)
- Categories, locations, groups, wanted requests, clothing details, and fit profiles
- Listings generated from inventory items
- Lending transaction lifecycle with item status syncing
- Inventory movement and condition logs
- QR payload generation per inventory item
- Search helper APIs for portal/mobile clients
- Desk form actions (create listing/start lending from item form)
- Auto-seeded workspace, categories, locations, and roles on install/migrate
- Lending workflow bootstrap for approval → checkout → return

## App Setup

From your Frappe Bench:

```bash
bench get-app /Users/hunterhalloran/Documents/New\ project
bench --site your-site install-app shwap
bench --site your-site migrate
```

After migrate, open the `Shwap` workspace in Desk.

## Quick Validation

From this repo:

```bash
python3 -m compileall shwap
python3 -m unittest shwap.tests.test_fit
```

## Key API Methods

- `shwap.api.quick_add_item`
- `shwap.api.create_listing_from_item`
- `shwap.api.start_lending_transaction`
- `shwap.api.search_inventory`
- `shwap.api.dashboard_summary`
- `shwap.api.lending_queue`
- `shwap.api.estimate_fit_for_item`

## First Push Checklist

- Verify app install and migrate on a test site.
- Confirm `Shwap` workspace is visible in Desk.
- Confirm quick-add, create listing, and start lending actions work.
- Run compile and unit checks above.
