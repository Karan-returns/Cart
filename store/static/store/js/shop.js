const customerInput = document.getElementById("customer-id");
const productsGrid = document.getElementById("products-grid");
const cartItemsEl = document.getElementById("cart-items");
const cartSubtotalEl = document.getElementById("cart-subtotal");
const cartCountEl = document.getElementById("cart-count");
const checkoutBtn = document.getElementById("checkout-btn");
const applyDiscountBtn = document.getElementById("apply-discount-btn");
const discountInput = document.getElementById("discount-code");
const discountMessage = document.getElementById("discount-message");
const checkoutSummary = document.getElementById("checkout-summary");
const cartDiscountEl = document.getElementById("cart-discount");
const cartTotalEl = document.getElementById("cart-total");

let appliedDiscountCode = null;
const orderResult = document.getElementById("order-result");
const orderDetails = document.getElementById("order-details");
const newDiscountBanner = document.getElementById("new-discount-banner");
const customerStats = document.getElementById("customer-stats");
const orderCountBadge = document.getElementById("order-count-badge");
const totalSpentBadge = document.getElementById("total-spent-badge");
const milestoneBadge = document.getElementById("milestone-badge");
const availableCodesEl = document.getElementById("available-codes");
const purchaseHistory = document.getElementById("purchase-history");
const historyList = document.getElementById("history-list");
const historyOrderCount = document.getElementById("history-order-count");

function getCustomerId() {
  const id = customerInput.value.trim();
  if (!id) {
    throw new Error("Please enter your name to shop.");
  }
  return id;
}

function saveCustomerId() {
  const id = customerInput.value.trim();
  if (id) {
    localStorage.setItem("customerId", id);
  }
}

function loadCustomerId() {
  const saved = localStorage.getItem("customerId");
  if (saved) {
    customerInput.value = saved;
  }
}

async function loadProducts() {
  productsGrid.innerHTML = '<p class="muted">Loading products…</p>';
  try {
    const products = await apiRequest("/products/");
    productsGrid.innerHTML = products
      .map(
        (p) => `
      <article class="product-card" data-product-id="${p.id}">
        <h3>${escapeHtml(p.name)}</h3>
        <div class="product-price">${formatMoney(p.price)}</div>
        <div class="product-actions">
          <input type="number" class="input qty-input" value="1" min="1" max="99"
                 aria-label="Quantity for ${escapeHtml(p.name)}">
          <button type="button" class="btn btn-primary btn-sm add-to-cart">Add</button>
        </div>
      </article>`
      )
      .join("");
  } catch (err) {
    productsGrid.innerHTML = `<p class="muted">${escapeHtml(err.message)}</p>`;
  }
}

async function loadCart() {
  let customerId;
  try {
    customerId = getCustomerId();
  } catch {
    renderEmptyCart();
    hideCustomerProfile();
    return;
  }

  try {
    const cart = await apiRequest(`/carts/${encodeURIComponent(customerId)}/`);
    renderCart(cart);
    await loadCustomerProfile(customerId);
  } catch (err) {
    showToast(err.message, "error");
  }
}

function hideCustomerProfile() {
  customerStats.hidden = true;
  purchaseHistory.hidden = true;
  availableCodesEl.hidden = true;
}

async function loadCustomerProfile(customerId) {
  try {
    const profile = await apiRequest(
      `/customers/${encodeURIComponent(customerId)}/profile/`
    );
    renderCustomerProfile(profile);
  } catch {
    hideCustomerProfile();
  }
}

function renderAvailableCodes(codes) {
  if (!codes.length) {
    availableCodesEl.hidden = true;
    return;
  }

  availableCodesEl.hidden = false;
  availableCodesEl.innerHTML = `
    <div class="available-codes-title">Your unused discount codes</div>
    <ul class="available-codes-list">
      ${codes
        .map(
          (code) => `
        <li>
          <button type="button" class="code-chip" data-code="${escapeHtml(code.code)}">
            <strong>${escapeHtml(code.code)}</strong>
            <span>${code.percent}% off</span>
          </button>
        </li>`
        )
        .join("")}
    </ul>`;
}

function renderCustomerProfile(profile) {
  const count = profile.order_count;
  customerStats.hidden = false;
  orderCountBadge.textContent = `${count} order${count !== 1 ? "s" : ""} placed`;
  totalSpentBadge.textContent = `${formatMoney(profile.total_spent)} spent`;

  const storeOrders = profile.store_completed_orders ?? 0;
  const everyN = profile.discount_every_n_orders ?? window.STORE_CONFIG.discountEveryN;
  const untilNext = profile.orders_until_next_reward ?? everyN;
  if (untilNext === 0) {
    milestoneBadge.textContent = `Store order #${storeOrders} — reward unlocked`;
    milestoneBadge.className = "badge badge-success";
  } else {
    milestoneBadge.textContent = `${untilNext} store order${untilNext !== 1 ? "s" : ""} until next reward`;
    milestoneBadge.className = "badge badge-muted";
  }

  renderAvailableCodes(profile.available_discount_codes || []);

  if (count === 0) {
    purchaseHistory.hidden = true;
    return;
  }

  purchaseHistory.hidden = false;
  historyOrderCount.textContent = `${count} order${count !== 1 ? "s" : ""}`;
  historyList.innerHTML = profile.orders
    .slice()
    .reverse()
    .map((order) => renderOrderCard(order))
    .join("");
}

function renderOrderCard(order) {
  const itemsHtml = order.items
    .map(
      (item) =>
        `<li>${escapeHtml(item.product_name)} × ${item.quantity} — ${formatMoney(item.line_total)}</li>`
    )
    .join("");

  const discountLine =
    parseFloat(order.discount_amount) > 0
      ? `<div class="history-meta">Discount (${escapeHtml(order.discount_code || "")}): -${formatMoney(order.discount_amount)}</div>`
      : "";

  const date = new Date(order.created_at).toLocaleString();

  return `
    <article class="history-card">
      <div class="history-card-header">
        <span class="history-date">${escapeHtml(date)}</span>
        <strong>${formatMoney(order.total)}</strong>
      </div>
      <ul class="history-items">${itemsHtml}</ul>
      ${discountLine}
    </article>`;
}

function clearDiscountPreview() {
  appliedDiscountCode = null;
  discountInput.value = "";
  discountInput.disabled = false;
  discountMessage.hidden = true;
  checkoutSummary.hidden = true;
  applyDiscountBtn.disabled = true;
  applyDiscountBtn.textContent = "Apply";
}

function showDiscountMessage(text, type) {
  discountMessage.hidden = false;
  discountMessage.textContent = text;
  discountMessage.className = `discount-message ${type}`;
}

function renderCheckoutSummary(preview) {
  if (preview.discount_applied) {
    checkoutSummary.hidden = false;
    cartDiscountEl.textContent = `-${formatMoney(preview.discount_amount)} (${preview.discount_percent}% off)`;
    cartTotalEl.textContent = formatMoney(preview.total);
    showDiscountMessage(
      `Code "${preview.discount_code}" applied successfully.`,
      "success"
    );
    applyDiscountBtn.textContent = "Applied";
    applyDiscountBtn.disabled = true;
    discountInput.disabled = true;
  } else {
    checkoutSummary.hidden = true;
    cartTotalEl.textContent = formatMoney(preview.subtotal);
    applyDiscountBtn.textContent = "Apply";
    applyDiscountBtn.disabled = !discountInput.value.trim();
    discountInput.disabled = false;
  }
}

function renderEmptyCart() {
  cartItemsEl.innerHTML = '<p class="muted empty-state">Cart is empty</p>';
  cartSubtotalEl.textContent = formatMoney(0);
  cartCountEl.textContent = "0 items";
  checkoutBtn.disabled = true;
  clearDiscountPreview();
}

function renderCart(cart) {
  if (!cart.items.length) {
    renderEmptyCart();
    return;
  }

  const totalQty = cart.items.reduce((sum, item) => sum + item.quantity, 0);
  cartCountEl.textContent = `${totalQty} item${totalQty !== 1 ? "s" : ""}`;
  cartSubtotalEl.textContent = formatMoney(cart.subtotal);

  cartItemsEl.innerHTML = cart.items
    .map(
      (item) => `
    <div class="cart-line">
      <div>
        <div class="cart-line-name">${escapeHtml(item.product_name)}</div>
        <div class="cart-line-meta">${item.quantity} × ${formatMoney(item.unit_price)}</div>
      </div>
      <div class="cart-line-price">${formatMoney(item.line_total)}</div>
    </div>`
    )
    .join("");

  checkoutBtn.disabled = false;
  applyDiscountBtn.disabled = !discountInput.value.trim() && !appliedDiscountCode;

  if (appliedDiscountCode) {
    discountInput.value = appliedDiscountCode;
    fetchDiscountPreview(appliedDiscountCode, { silent: true }).catch(() => {
      clearDiscountPreview();
    });
  }
}

async function fetchDiscountPreview(code, { silent = false } = {}) {
  const customerId = getCustomerId();
  const preview = await apiRequest("/checkout/preview/", {
    method: "POST",
    body: JSON.stringify({ customer_id: customerId, discount_code: code }),
  });

  if (!preview.discount_applied) {
    throw new Error("No discount applied.");
  }

  appliedDiscountCode = preview.discount_code;
  renderCheckoutSummary(preview);
  if (!silent) {
    showToast("Discount applied — review total before checkout");
  }
  return preview;
}

async function applyDiscount() {
  const code = discountInput.value.trim();
  if (!code) {
    showToast("Enter a discount code", "error");
    return;
  }

  applyDiscountBtn.disabled = true;
  try {
    await fetchDiscountPreview(code);
  } catch (err) {
    appliedDiscountCode = null;
    checkoutSummary.hidden = true;
    showDiscountMessage(err.message, "error");
    applyDiscountBtn.disabled = false;
    discountInput.disabled = false;
    applyDiscountBtn.textContent = "Apply";
  }
}

async function addToCart(productId, quantity) {
  const customerId = getCustomerId();
  saveCustomerId();

  await apiRequest(`/carts/${encodeURIComponent(customerId)}/items/`, {
    method: "POST",
    body: JSON.stringify({ product_id: productId, quantity }),
  });

  showToast("Added to cart");
  await loadCart();
}

async function checkout() {
  const customerId = getCustomerId();
  saveCustomerId();

  const body = { customer_id: customerId };
  if (appliedDiscountCode) {
    body.discount_code = appliedDiscountCode;
  }

  checkoutBtn.disabled = true;
  try {
    const result = await apiRequest("/checkout/", {
      method: "POST",
      body: JSON.stringify(body),
    });

    showOrderResult(result);
    clearDiscountPreview();
    await loadCart();
    await loadCustomerProfile(customerId);
    if (result.newly_issued_discount_code) {
      showToast(
        `Milestone reached! Your code: ${result.newly_issued_discount_code.code}`,
        "success"
      );
    } else {
      showToast("Order placed successfully!");
    }
  } catch (err) {
    showToast(err.message, "error");
    checkoutBtn.disabled = false;
  }
}

function showOrderResult(result) {
  const order = result.order;
  orderResult.hidden = false;

  const itemsHtml = order.items
    .map(
      (item) => `
    <div class="row">
      <span>${escapeHtml(item.product_name)} × ${item.quantity}</span>
      <span>${formatMoney(item.line_total)}</span>
    </div>`
    )
    .join("");

  orderDetails.innerHTML = `
    <div class="order-summary">
      ${itemsHtml}
      <div class="row"><span>Subtotal</span><span>${formatMoney(order.subtotal)}</span></div>
      ${
        parseFloat(order.discount_amount) > 0
          ? `<div class="row"><span>Discount (${escapeHtml(order.discount_code || "")})</span><span>-${formatMoney(order.discount_amount)}</span></div>`
          : ""
      }
      <div class="row total"><span>Total paid</span><span>${formatMoney(order.total)}</span></div>
    </div>`;

  if (result.newly_issued_discount_code) {
    const dc = result.newly_issued_discount_code;
    newDiscountBanner.hidden = false;
    newDiscountBanner.innerHTML = `
      <div class="discount-banner-title">Milestone reached!</div>
      <p>You earned a <strong>${dc.percent}%</strong> discount code for your next order:</p>
      <div class="discount-banner-code">${escapeHtml(dc.code)}</div>
      <button type="button" class="btn btn-secondary btn-sm" id="use-new-discount-btn">
        Use this code
      </button>`;
    document.getElementById("use-new-discount-btn")?.addEventListener("click", () => {
      discountInput.value = dc.code;
      applyDiscountBtn.disabled = false;
      applyDiscount();
    });
  } else {
    newDiscountBanner.hidden = true;
  }

  orderResult.hidden = false;
  orderResult.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

productsGrid.addEventListener("click", async (e) => {
  const btn = e.target.closest(".add-to-cart");
  if (!btn) return;

  const card = btn.closest(".product-card");
  const productId = card.dataset.productId;
  const qtyInput = card.querySelector(".qty-input");
  const quantity = parseInt(qtyInput.value, 10) || 1;

  btn.disabled = true;
  try {
    await addToCart(productId, quantity);
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    btn.disabled = false;
  }
});

function onCustomerChange() {
  saveCustomerId();
  loadCart();
}

customerInput.addEventListener("change", onCustomerChange);
customerInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") onCustomerChange();
});

discountInput.addEventListener("input", () => {
  if (appliedDiscountCode) return;
  applyDiscountBtn.disabled = !discountInput.value.trim();
  discountMessage.hidden = true;
});

discountInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !appliedDiscountCode) {
    e.preventDefault();
    applyDiscount();
  }
});

availableCodesEl.addEventListener("click", (e) => {
  const chip = e.target.closest(".code-chip");
  if (!chip) return;
  discountInput.value = chip.dataset.code;
  applyDiscountBtn.disabled = false;
  applyDiscount();
});

document.getElementById("refresh-products").addEventListener("click", loadProducts);
applyDiscountBtn.addEventListener("click", applyDiscount);
checkoutBtn.addEventListener("click", checkout);

loadCustomerId();
loadProducts();
loadCart();
