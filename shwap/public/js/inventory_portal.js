(function () {
  const root = document.getElementById("shwapPortal");
  if (!root || typeof frappe === "undefined") return;

  const page = root.dataset.page;

  function toPayload(form) {
    const formData = new FormData(form);
    return Object.fromEntries(formData.entries());
  }

  async function submitWithReload(event, method, payloadBuilder) {
    event.preventDefault();
    const payload = payloadBuilder(event.target);
    await frappe.call({
      method,
      args: { payload },
    });
    window.location.reload();
  }

  function bindQuickAdd() {
    const form = document.getElementById("quickAddForm");
    if (!form) return;
    form.addEventListener("submit", (event) =>
      submitWithReload(event, "shwap.api.portal_quick_add_item", toPayload)
    );
  }

  function bindSearch() {
    const form = document.getElementById("searchForm");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = toPayload(form);
      const response = await frappe.call({
        method: "shwap.api.search_inventory",
        args: {
          query: payload.query || "",
          status: payload.status || "",
          location: payload.location || "",
        },
      });
      const rows = response.message || [];
      const wrap = document.getElementById("itemsTableWrap");
      if (!wrap) return;

      const body =
        rows.length === 0
          ? `<tr><td colspan="5" class="muted">No matching items.</td></tr>`
          : rows
              .map(
                (row) =>
                  `<tr>
                    <td><a href="/app/inventory-item/${encodeURIComponent(row.name)}" target="_blank">${row.item_name}</a></td>
                    <td>${row.category || ""}</td>
                    <td>${row.location || ""}</td>
                    <td>${row.status || ""}</td>
                    <td>${row.condition || ""}</td>
                  </tr>`
              )
              .join("");

      wrap.innerHTML = `
        <table class="portal-table">
          <thead><tr><th>Item</th><th>Category</th><th>Location</th><th>Status</th><th>Condition</th></tr></thead>
          <tbody>${body}</tbody>
        </table>
      `;
    });
  }

  function bindPrefillButtons() {
    document.querySelectorAll("[data-prefill-listing]").forEach((button) => {
      button.addEventListener("click", () => {
        const item = button.dataset.prefillListing;
        window.location.href = `/inventory-listings?item=${encodeURIComponent(item)}`;
      });
    });

    document.querySelectorAll("[data-prefill-lending]").forEach((button) => {
      button.addEventListener("click", () => {
        const item = button.dataset.prefillLending;
        window.location.href = `/inventory-lending?item=${encodeURIComponent(item)}`;
      });
    });
  }

  function preselectFromQuery(selectId, queryKey) {
    const select = document.getElementById(selectId);
    if (!select) return;
    const value = new URLSearchParams(window.location.search).get(queryKey);
    if (!value) return;
    select.value = value;
  }

  function bindListing() {
    const form = document.getElementById("listingForm");
    if (!form) return;
    preselectFromQuery("listingItem", "item");
    form.addEventListener("submit", (event) =>
      submitWithReload(event, "shwap.api.portal_create_listing", toPayload)
    );
  }

  function bindLending() {
    const form = document.getElementById("lendingForm");
    if (!form) return;
    preselectFromQuery("lendingItem", "item");
    form.addEventListener("submit", (event) =>
      submitWithReload(event, "shwap.api.portal_start_lending", toPayload)
    );

    document.querySelectorAll("[data-lending-status]").forEach((button) => {
      button.addEventListener("click", async () => {
        await frappe.call({
          method: "shwap.api.portal_update_lending_status",
          args: {
            name: button.dataset.lendingStatus,
            status: button.dataset.status,
          },
        });
        window.location.reload();
      });
    });
  }

  function bindRequests() {
    const form = document.getElementById("wantedForm");
    if (!form) return;
    form.addEventListener("submit", (event) =>
      submitWithReload(event, "shwap.api.portal_create_wanted_request", toPayload)
    );
  }

  function bindWardrobe() {
    const fitForm = document.getElementById("fitProfileForm");
    if (fitForm) {
      fitForm.addEventListener("submit", (event) =>
        submitWithReload(event, "shwap.api.portal_create_fit_profile", toPayload)
      );
    }

    const clothingForm = document.getElementById("clothingForm");
    if (clothingForm) {
      clothingForm.addEventListener("submit", (event) =>
        submitWithReload(event, "shwap.api.portal_create_clothing_detail", toPayload)
      );
    }

    const fitEstimateForm = document.getElementById("fitEstimateForm");
    if (fitEstimateForm) {
      fitEstimateForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = toPayload(fitEstimateForm);
        const response = await frappe.call({
          method: "shwap.api.estimate_fit_for_item",
          args: {
            clothing_detail: payload.clothing_detail,
            fit_profile: payload.fit_profile,
          },
        });
        const result = response.message || {};
        const target = document.getElementById("fitEstimateResult");
        if (target) {
          target.textContent = `${result.fit_result || ""} — ${result.explanation || ""}`;
        }
      });
    }
  }

  if (page === "inventory-items") {
    bindQuickAdd();
    bindSearch();
    bindPrefillButtons();
  } else if (page === "inventory-listings") {
    bindListing();
  } else if (page === "inventory-lending") {
    bindLending();
  } else if (page === "inventory-requests") {
    bindRequests();
  } else if (page === "inventory-wardrobe") {
    bindWardrobe();
  }
})();
