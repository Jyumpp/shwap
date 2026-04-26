frappe.ui.form.on("Lending Transaction", {
  refresh(frm) {
    if (!frm.is_new() && frm.doc.inventory_item) {
      frm.add_custom_button(__("Open Item"), () => {
        frappe.set_route("Form", "Inventory Item", frm.doc.inventory_item);
      });
    }

    if (!frm.is_new()) {
      frm.add_custom_button(__("Mark Checked Out"), async () => {
        await frm.set_value("status", "Checked out");
        await frm.save();
      });

      frm.add_custom_button(__("Mark Returned"), async () => {
        await frm.set_value("status", "Returned accepted");
        await frm.set_value("return_date", frappe.datetime.get_today());
        await frm.save();
      });

      frm.add_custom_button(__("Mark Overdue"), async () => {
        await frm.set_value("status", "Overdue");
        await frm.save();
      });
    }
  },
});
