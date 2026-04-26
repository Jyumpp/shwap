const ITEM_TYPE_OPTIONS = {
  tools: ["Power Tool", "Hand Tool", "Yard Tool", "Workshop Equipment"],
  leisure: ["Sports Equipment", "Camping Gear", "Gaming Console", "Board Game", "Hobby Gear"],
  clothing: ["Top", "Bottom", "Outerwear", "Shoe", "Accessory"],
  electronics: ["Computer", "Phone", "Audio Device", "Camera", "Peripheral"],
  household: ["Kitchen Item", "Furniture", "Appliance", "Storage"],
  books_media: ["Book", "Movie", "Music", "Collectible"],
  default: ["General"],
};

function normalizedCategory(category) {
  const text = (category || "").toLowerCase();
  if (text.includes("tool")) return "tools";
  if (text.includes("leisure") || text.includes("sport") || text.includes("camp") || text.includes("game")) return "leisure";
  if (text.includes("cloth") || text.includes("shoe") || text.includes("wear") || text.includes("accessor")) return "clothing";
  if (text.includes("electronic") || text.includes("computer") || text.includes("phone")) return "electronics";
  if (text.includes("household") || text.includes("kitchen") || text.includes("furniture")) return "household";
  if (text.includes("book") || text.includes("media")) return "books_media";
  return "default";
}

function applyCategoryOptions(frm) {
  const categoryKey = normalizedCategory(frm.doc.category);
  const options = ITEM_TYPE_OPTIONS[categoryKey] || ITEM_TYPE_OPTIONS.default;
  frm.set_df_property("item_type", "options", ["", ...options].join("\n"));

  if (frm.doc.item_type && !options.includes(frm.doc.item_type)) {
    frm.set_value("item_type", "");
  }
}

function addClothingDetailButton(frm) {
  const isClothing = normalizedCategory(frm.doc.category) === "clothing";
  if (!isClothing) return;

  frm.add_custom_button(__("Manage Clothing Detail"), async () => {
    if (frm.is_new()) {
      frappe.msgprint(__("Save the Inventory Item first."));
      return;
    }

    const existing = await frappe.db.get_value("Clothing Detail", { inventory_item: frm.doc.name }, "name");
    const detailName = existing?.message?.name;

    if (detailName) {
      frappe.set_route("Form", "Clothing Detail", detailName);
      return;
    }

    frappe.new_doc("Clothing Detail", {
      inventory_item: frm.doc.name,
      garment_type: frm.doc.item_type || "",
      label_size: "",
    });
  });
}

frappe.ui.form.on("Inventory Item", {
  setup(frm) {
    applyCategoryOptions(frm);
  },

  category(frm) {
    applyCategoryOptions(frm);
  },

  refresh(frm) {
    applyCategoryOptions(frm);

    if (frm.is_new()) {
      return;
    }

    frm.add_custom_button(__("Create Listing"), async () => {
      const values = await frappe.prompt(
        [
          {
            fieldname: "listing_type",
            label: __("Listing Type"),
            fieldtype: "Select",
            options: ["Sell", "Trade", "Swap", "Lend", "Gift", "Rent"].join("\n"),
            reqd: 1,
          },
          {
            fieldname: "listing_status",
            label: __("Listing Status"),
            fieldtype: "Select",
            options: ["Draft", "Active", "Paused"].join("\n"),
            default: "Draft",
            reqd: 1,
          },
          {
            fieldname: "price",
            label: __("Price"),
            fieldtype: "Currency",
          },
        ],
        __("Create Listing"),
        __("Create")
      );

      if (!values) {
        return;
      }

      const response = await frappe.call({
        method: "shwap.api.create_listing_from_item",
        args: {
          item: frm.doc.name,
          listing_type: values.listing_type,
          payload: {
            listing_status: values.listing_status,
            price: values.price || 0,
          },
        },
      });

      if (response && response.message && response.message.name) {
        frappe.set_route("Form", "Listing", response.message.name);
      }
    });

    frm.add_custom_button(__("Start Lending"), async () => {
      const values = await frappe.prompt(
        [
          {
            fieldname: "borrower",
            label: __("Borrower"),
            fieldtype: "Link",
            options: "User",
            reqd: 1,
          },
          {
            fieldname: "due_date",
            label: __("Due Date"),
            fieldtype: "Date",
            reqd: 1,
          },
          {
            fieldname: "deposit_amount",
            label: __("Deposit"),
            fieldtype: "Currency",
          },
        ],
        __("Start Lending"),
        __("Create")
      );

      if (!values) {
        return;
      }

      const response = await frappe.call({
        method: "shwap.api.start_lending_transaction",
        args: {
          item: frm.doc.name,
          borrower: values.borrower,
          due_date: values.due_date,
          payload: {
            deposit_amount: values.deposit_amount || 0,
          },
        },
      });

      if (response && response.message && response.message.name) {
        frappe.set_route("Form", "Lending Transaction", response.message.name);
      }
    });

    frm.add_custom_button(__("Open QR Link"), () => {
      if (!frm.doc.qr_payload) {
        frappe.msgprint(__("No QR payload found for this item."));
        return;
      }
      window.open(frm.doc.qr_payload, "_blank");
    });

    addClothingDetailButton(frm);
  },

  before_save(frm) {
    if (!frm.doc.owner_user) {
      frm.set_value("owner_user", frappe.session.user);
    }
    if (!frm.doc.current_holder) {
      frm.set_value("current_holder", frappe.session.user);
    }
  },
});
