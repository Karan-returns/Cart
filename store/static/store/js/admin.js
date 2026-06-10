const adminKeyInput = document.getElementById("admin-key");
const saveKeyBtn = document.getElementById("save-admin-key");
const refreshBtn = document.getElementById("refresh-stats");
const generateBtn = document.getElementById("generate-discount");
const generateResult = document.getElementById("generate-result");
const settingsForm = document.getElementById("settings-form");
const refreshSettingsBtn = document.getElementById("refresh-settings");
const refreshCustomersBtn = document.getElementById("refresh-customers");
const customersTableWrap = document.getElementById("customers-table-wrap");
const customerDetailPanel = document.getElementById("customer-detail-panel");
const detailCustomerName = document.getElementById("detail-customer-name");
const customerDetailSummary = document.getElementById("customer-detail-summary");
const customerOrdersList = document.getElementById("customer-orders-list");
const closeDetailBtn = document.getElementById("close-detail");

const statEls = {
  items: document.getElementById("stat-items"),
  revenue: document.getElementById("stat-revenue"),
  issued: document.getElementById("stat-issued"),
  used: document.getElementById("stat-used"),
  discounts: document.getElementById("stat-discounts"),
};

function getAdminKey() {
  const key = sessionStorage.getItem("adminApiKey") || adminKeyInput.value.trim();
  if (!key) {
    throw new Error("Please enter and save your admin API key.");
  }
  return key;
}

function adminHeaders() {
  return { "X-Admin-Key": getAdminKey() };
}

function loadSavedKey() {
  const saved = sessionStorage.getItem("adminApiKey");
  if (saved) {
    adminKeyInput.value = saved;
  }
}

function saveAdminKey() {
  const key = adminKeyInput.value.trim();
  if (!key) {
    showToast("Enter an API key first", "error");
    return;
  }
  sessionStorage.setItem("adminApiKey", key);
  showToast("Admin key saved");
  refreshAll();
}

async function refreshAll() {
  await Promise.all([loadStats(), loadSettings(), loadCustomers()]);
}

async function loadStats() {
  try {
    const stats = await apiRequest("/admin/stats/", { headers: adminHeaders() });
    statEls.items.textContent = stats.items_purchased;
    statEls.revenue.textContent = formatMoney(stats.revenue);
    statEls.issued.textContent = stats.discount_codes_issued;
    statEls.used.textContent = stats.discount_codes_used;
    statEls.discounts.textContent = formatMoney(stats.total_discounts_given);
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function loadSettings() {
  try {
    const settings = await apiRequest("/admin/settings/", { headers: adminHeaders() });
    document.getElementById("setting-n").value = settings.discount_every_n_orders;
    document.getElementById("setting-percent").value = settings.discount_percent;
    document.getElementById("setting-prefix").value = settings.discount_code_prefix;
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function saveSettings(e) {
  e.preventDefault();
  try {
    const body = {
      discount_every_n_orders: parseInt(document.getElementById("setting-n").value, 10),
      discount_percent: parseInt(document.getElementById("setting-percent").value, 10),
      discount_code_prefix: document.getElementById("setting-prefix").value.trim(),
    };
    await apiRequest("/admin/settings/", {
      method: "PATCH",
      headers: adminHeaders(),
      body: JSON.stringify(body),
    });
    showToast("Settings saved");
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function loadCustomers() {
  try {
    const data = await apiRequest("/admin/customers/", { headers: adminHeaders() });
    renderCustomersTable(data.customers);
  } catch (err) {
    customersTableWrap.innerHTML = `<p class="muted">${escapeHtml(err.message)}</p>`;
  }
}

function renderCustomersTable(customers) {
  if (!customers.length) {
    customersTableWrap.innerHTML = '<p class="muted">No customers have placed orders yet.</p>';
    return;
  }

  const rows = customers
    .map(
      (c) => `
    <tr data-customer-id="${escapeHtml(c.customer_id)}">
      <td><strong>${escapeHtml(c.customer_id)}</strong></td>
      <td>${c.order_count}</td>
      <td>${c.items_purchased}</td>
      <td>${formatMoney(c.total_spent)}</td>
      <td>${c.last_order_at ? escapeHtml(new Date(c.last_order_at).toLocaleString()) : "—"}</td>
      <td><button type="button" class="btn btn-ghost btn-sm view-customer">View</button></td>
    </tr>`
    )
    .join("");

  customersTableWrap.innerHTML = `
    <div class="table-scroll">
      <table class="data-table">
        <thead>
          <tr>
            <th>Customer</th>
            <th>Orders</th>
            <th>Items</th>
            <th>Total Spent</th>
            <th>Last Order</th>
            <th></th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

async function showCustomerDetail(customerId) {
  try {
    const detail = await apiRequest(
      `/admin/customers/${encodeURIComponent(customerId)}/`,
      { headers: adminHeaders() }
    );

    detailCustomerName.textContent = detail.customer_id;
    customerDetailSummary.innerHTML = `
      <div class="detail-stats">
        <span class="badge">${detail.order_count} orders</span>
        <span class="badge">${detail.items_purchased} items</span>
        <span class="badge badge-success">${formatMoney(detail.total_spent)} spent</span>
      </div>`;

    customerOrdersList.innerHTML = detail.orders
      .slice()
      .reverse()
      .map((order) => {
        const items = order.items
          .map(
            (item) =>
              `<li>${escapeHtml(item.product_name)} × ${item.quantity} — ${formatMoney(item.line_total)}</li>`
          )
          .join("");
        const discount =
          parseFloat(order.discount_amount) > 0
            ? `<div class="history-meta">Discount: -${formatMoney(order.discount_amount)}</div>`
            : "";
        return `
          <article class="history-card">
            <div class="history-card-header">
              <span class="history-date">${escapeHtml(new Date(order.created_at).toLocaleString())}</span>
              <strong>${formatMoney(order.total)}</strong>
            </div>
            <ul class="history-items">${items}</ul>
            ${discount}
          </article>`;
      })
      .join("");

    customerDetailPanel.hidden = false;
    customerDetailPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function generateDiscount() {
  generateResult.hidden = true;
  generateBtn.disabled = true;

  try {
    const result = await apiRequest("/admin/discount-codes/generate/", {
      method: "POST",
      headers: adminHeaders(),
    });

    generateResult.hidden = false;
    generateResult.className = "generate-result success";
    generateResult.innerHTML = `
      <div>${escapeHtml(result.message)}</div>
      <div class="code">${escapeHtml(result.code)}</div>
      <div class="muted" style="margin-top:0.5rem">${result.percent}% off · issued at order #${result.issued_for_order_number}</div>`;

    showToast("Discount code generated");
    await loadStats();
  } catch (err) {
    generateResult.hidden = false;
    generateResult.className = "generate-result error";
    generateResult.textContent = err.message;
    showToast(err.message, "error");
  } finally {
    generateBtn.disabled = false;
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

saveKeyBtn.addEventListener("click", saveAdminKey);
refreshBtn.addEventListener("click", loadStats);
refreshSettingsBtn.addEventListener("click", loadSettings);
refreshCustomersBtn.addEventListener("click", loadCustomers);
generateBtn.addEventListener("click", generateDiscount);
settingsForm.addEventListener("submit", saveSettings);
closeDetailBtn.addEventListener("click", () => {
  customerDetailPanel.hidden = true;
});

customersTableWrap.addEventListener("click", (e) => {
  const btn = e.target.closest(".view-customer");
  if (!btn) return;
  const row = btn.closest("tr");
  showCustomerDetail(row.dataset.customerId);
});

loadSavedKey();
if (sessionStorage.getItem("adminApiKey")) {
  refreshAll();
}
