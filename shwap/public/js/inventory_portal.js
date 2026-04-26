(function () {
  const root = document.getElementById("shwapPortal");
  if (!root) return;

  const initialData = JSON.parse(root.dataset.initial || "{}");
  let state = initialData;

  const metricGrid = document.getElementById("metricGrid");
  const itemsTable = document.getElementById("itemsTable");
  const listingsTable = document.getElementById("listingsTable");
  const lendingTable = document.getElementById("lendingTable");
  const requestsTable = document.getElementById("requestsTable");
  const fitProfilesTable = document.getElementById("fitProfilesTable");
  const clothingTable = document.getElementById("clothingTable");
  const fitEstimateResult = document.getElementById("fitEstimateResult");

  function number(value) {
    return Number(value || 0).toLocaleString();
  }

  function table(columns, rows, emptyText) {
    if (!rows || !rows.length) {
      return `<div class="muted">${emptyText}</div>`;
    }
    const head = `<tr>${columns.map((col) => `<th>${col.label}</th>`).join("")}</tr>`;
    const body = rows
      .map((row) => `<tr>${columns.map((col) => `<td>${col.render ? col.render(row[col.key], row) : (row[col.key] ?? "")}</td>`).join("")}</tr>`)
      .join("");
    return `<table class="table"><thead>${head}</thead><tbody>${body}</tbody></table>`;
  }

  function render() {
    const summary = state.summary || {};
    metricGrid.innerHTML = `
      <article class="metric"><strong>${number(summary.total_items)}</strong><span>Total Items</span></article>
      <article class="metric"><strong>${number(summary.lent_out)}</strong><span>Lent Out</span></article>
      <article class="metric"><strong>${number(summary.active_listings)}</strong><span>Active Listings</span></article>
      <article class="metric"><strong>${number(summary.open_requests)}</strong><span>Open Requests</span></article>
    `;

    itemsTable.innerHTML = table(
      [
        { key: "item_name", label: "Item" },
        { key: "category", label: "Category" },
        { key: "location", label: "Location" },
        { key: "status", label: "Status" },
        {
          key: "name",
          label: "Actions",
          render: (_value, row) =>
            `<button class="action-btn" data-action="list" data-item="${row.name}">List</button>
             <button class="action-btn" data-action="lend" data-item="${row.name}">Lend</button>`,
        },
      ],
      state.items || [],
      "No items yet."
    );

    listingsTable.innerHTML = table(
      [
        { key: "title", label: "Title" },
        { key: "listing_type", label: "Type" },
        { key: "listing_status", label: "Status" },
        { key: "price", label: "Price", render: (value) => (value ? `$${Number(value).toFixed(2)}` : "-") },
      ],
      state.listings || [],
      "No listings yet."
    );

    lendingTable.innerHTML = table(
      [
        { key: "inventory_item", label: "Item" },
        { key: "borrower", label: "Borrower" },
        { key: "status", label: "Status" },
        { key: "due_date", label: "Due Date" },
        {
          key: "name",
          label: "Actions",
          render: (_value, row) =>
            `<button class="action-btn" data-action="lending-status" data-status="Checked out" data-name="${row.name}">Checked out</button>
             <button class="action-btn" data-action="lending-status" data-status="Returned accepted" data-name="${row.name}">Returned</button>`,
        },
      ],
      state.lending || [],
      "No lending records."
    );

    requestsTable.innerHTML = table(
      [
        { key: "title", label: "Title" },
        { key: "request_type", label: "Type" },
        { key: "status", label: "Status" },
        { key: "budget", label: "Budget", render: (value) => (value ? `$${Number(value).toFixed(2)}` : "-") },
      ],
      state.requests || [],
      "No requests yet."
    );

    fitProfilesTable.innerHTML = table(
      [
        { key: "profile_name", label: "Profile" },
        { key: "preferred_fit", label: "Fit" },
        { key: "privacy_level", label: "Privacy" },
      ],
      state.fit_profiles || [],
      "No fit profiles yet."
    );

    clothingTable.innerHTML = table(
      [
        { key: "inventory_item", label: "Item" },
        { key: "garment_type", label: "Garment" },
        { key: "label_size", label: "Size" },
        { key: "waist", label: "Waist" },
        { key: "inseam", label: "Inseam" },
      ],
      state.clothing_details || [],
      "No clothing details yet."
    );

    const categoryOptions = (state.categories || []).map((entry) => `<option value="${entry}">${entry}</option>`).join("");
    const locationOptions = (state.locations || []).map((entry) => `<option value="${entry}">${entry}</option>`).join("");
    const itemOptions = (state.items || []).map((entry) => `<option value="${entry.name}">${entry.item_name} (${entry.name})</option>`).join("");
    const userOptions = (state.users || []).map((entry) => `<option value="${entry}">${entry}</option>`).join("");
    const fitProfileOptions = (state.fit_profiles || []).map((entry) => `<option value="${entry.name}">${entry.profile_name}</option>`).join("");
    const clothingOptions = (state.clothing_details || []).map((entry) => `<option value="${entry.name}">${entry.inventory_item} • ${entry.garment_type}</option>`).join("");

    document.getElementById("quickAddCategory").innerHTML = categoryOptions;
    document.getElementById("wantedCategory").innerHTML = `<option value="">Select</option>${categoryOptions}`;
    document.getElementById("quickAddLocation").innerHTML = locationOptions;
    document.getElementById("searchLocation").innerHTML = `<option value="">Any</option>${locationOptions}`;
    document.getElementById("listingItem").innerHTML = itemOptions;
    document.getElementById("lendingItem").innerHTML = itemOptions;
    document.getElementById("clothingItem").innerHTML = itemOptions;
    document.getElementById("lendingBorrower").innerHTML = userOptions;
    document.getElementById("fitProfileSelect").innerHTML = fitProfileOptions;
    document.getElementById("fitClothing").innerHTML = clothingOptions;

    bindDynamicActions();
  }

  async function refreshData() {
    const response = await frappe.call("shwap.api.portal_bootstrap");
    state = response.message || {};
    render();
  }

  function getFormData(form) {
    const formData = new FormData(form);
    return Object.fromEntries(formData.entries());
  }

  function bindDynamicActions() {
    root.querySelectorAll("[data-action='list']").forEach((button) => {
      button.addEventListener("click", () => {
        document.querySelector('[data-tab="listingsTab"]').click();
        document.getElementById("listingItem").value = button.dataset.item || "";
      });
    });

    root.querySelectorAll("[data-action='lend']").forEach((button) => {
      document.querySelector('[data-tab="lendingTab"]');
      button.addEventListener("click", () => {
        document.querySelector('[data-tab="lendingTab"]').click();
        document.getElementById("lendingItem").value = button.dataset.item || "";
      });
    });

    root.querySelectorAll("[data-action='lending-status']").forEach((button) => {
      button.addEventListener("click", async () => {
        await frappe.call({
          method: "shwap.api.portal_update_lending_status",
          args: {
            name: button.dataset.name,
            status: button.dataset.status,
          },
        });
        await refreshData();
      });
    });
  }

  document.getElementById("quickAddForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = getFormData(event.target);
    await frappe.call({
      method: "shwap.api.portal_quick_add_item",
      args: { payload },
    });
    event.target.reset();
    await refreshData();
  });

  document.getElementById("listingForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = getFormData(event.target);
    await frappe.call({
      method: "shwap.api.portal_create_listing",
      args: { payload },
    });
    event.target.reset();
    await refreshData();
  });

  document.getElementById("lendingForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = getFormData(event.target);
    await frappe.call({
      method: "shwap.api.portal_start_lending",
      args: { payload },
    });
    event.target.reset();
    await refreshData();
  });

  document.getElementById("wantedForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = getFormData(event.target);
    await frappe.call({
      method: "shwap.api.portal_create_wanted_request",
      args: { payload },
    });
    event.target.reset();
    await refreshData();
  });

  document.getElementById("fitProfileForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = getFormData(event.target);
    await frappe.call({
      method: "shwap.api.portal_create_fit_profile",
      args: { payload },
    });
    event.target.reset();
    await refreshData();
  });

  document.getElementById("clothingForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = getFormData(event.target);
    await frappe.call({
      method: "shwap.api.portal_create_clothing_detail",
      args: { payload },
    });
    event.target.reset();
    await refreshData();
  });

  document.getElementById("fitEstimateForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = getFormData(event.target);
    const response = await frappe.call({
      method: "shwap.api.estimate_fit_for_item",
      args: {
        clothing_detail: payload.clothing_detail,
        fit_profile: payload.fit_profile,
      },
    });
    const result = response.message || {};
    fitEstimateResult.textContent = `${result.fit_result || ""} — ${result.explanation || ""}`;
  });

  document.getElementById("searchForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = getFormData(event.target);
    const response = await frappe.call({
      method: "shwap.api.search_inventory",
      args: {
        query: payload.query || "",
        status: payload.status || "",
        location: payload.location || "",
      },
    });
    const results = response.message || [];
    itemsTable.innerHTML = table(
      [
        { key: "item_name", label: "Item" },
        { key: "category", label: "Category" },
        { key: "location", label: "Location" },
        { key: "status", label: "Status" },
        { key: "condition", label: "Condition" },
      ],
      results,
      "No matching items."
    );
  });

  root.querySelectorAll("[data-refresh]").forEach((button) => {
    button.addEventListener("click", refreshData);
  });

  document.getElementById("portalNav").querySelectorAll("button[data-tab]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("#portalNav button[data-tab]").forEach((entry) => entry.classList.remove("active"));
      button.classList.add("active");
      const tab = button.dataset.tab;
      document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.remove("active"));
      document.getElementById(tab).classList.add("active");
    });
  });

  render();
})();
