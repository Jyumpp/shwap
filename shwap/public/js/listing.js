frappe.ui.form.on("Listing", {
  refresh(frm) {
    if (!frm.is_new() && frm.doc.inventory_item) {
      frm.add_custom_button(__("Open Item"), () => {
        frappe.set_route("Form", "Inventory Item", frm.doc.inventory_item);
      });
    }

    if (!frm.is_new()) {
      frm.add_custom_button(__("Mark Active"), async () => {
        await frm.set_value("listing_status", "Active");
        await frm.save();
      });

      frm.add_custom_button(__("Mark Completed"), async () => {
        await frm.set_value("listing_status", "Completed");
        await frm.save();
      });
    }
  },
});
