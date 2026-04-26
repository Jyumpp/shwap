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

    const categoryOptions = (state.categories || []).map((entry) => `<option value="${entry}">${entry}</option>`).join("");
    const locationOptions = (state.locations || []).map((entry) => `<option value="${entry}">${entry}</option>`).join("");
    document.getElementById("quickAddCategory").innerHTML = categoryOptions;
    document.getElementById("wantedCategory").innerHTML = `<option value="">Select</option>${categoryOptions}`;
    document.getElementById("quickAddLocation").innerHTML = locationOptions;
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

  root.querySelectorAll("[data-refresh]").forEach((button) => {
    button.addEventListener("click", refreshData);
  });

  render();
})();
