frappe.listview_settings["Inventory Item"] = {
  onload(listview) {
    listview.page.add_inner_button(__("Quick Add Item"), () => {
      frappe.new_doc("Inventory Item");
    });
  },
  get_indicator(doc) {
    if (doc.status === "Lent out") return [__("Lent out"), "orange", "status,=,Lent out"];
    if (doc.status === "Listed") return [__("Listed"), "blue", "status,=,Listed"];
    if (doc.status === "Needs repair") return [__("Needs repair"), "red", "status,=,Needs repair"];
    if (doc.status === "Missing") return [__("Missing"), "red", "status,=,Missing"];
    return [__("Active"), "green", "status,=,Active"];
  },
};
