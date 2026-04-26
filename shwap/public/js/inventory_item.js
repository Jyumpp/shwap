frappe.ui.form.on("Inventory Item", {
  refresh(frm) {
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
