# Insurance Logic — POS Next

## Overview

Certain items sold via POS (e.g., insurance policies, warranty products) require:
1. A unique **Insurance Serial Number** to be captured at the point of sale.
2. An automatic **Purchase Receipt** to be created and submitted on the supplier's behalf immediately before the Sales Invoice is submitted.

This feature spans two apps: **pos_next** (POS UI + item API) and **auto_insurance** (backend PR creation hook).

---

## Custom Fields

### Item Category
> Defined in: `customization_iconcept` app

| Field Name | Type | Label | Purpose |
|---|---|---|---|
| `generate_auto_purchase_reciept` | Check | Generate Auto Purchase Reciept | When enabled, items in this category trigger the insurance serial capture flow and auto PR creation. **Note:** Field name has a deliberate typo ("reciept") — must be used exactly as spelled everywhere. |
| `category_supplier` | Link → Supplier | Category Supplier | The supplier against whom the auto Purchase Receipt is created. Mandatory when `generate_auto_purchase_reciept = 1`. |

### Sales Invoice Item
| Field Name | Type | Purpose |
|---|---|---|
| `custom_insurance_sr_no` | Data | Stores the insurance serial number entered by the cashier in POS. Saved per line item. |

### Purchase Receipt
| Field Name | Type | Purpose |
|---|---|---|
| `custom_invoice_attachment` | Attachment | Placeholder attachment path set on auto-created PRs (`/files/auto-pr-placeholder.txt`). Replaced when the actual supplier invoice arrives. |

---

## End-to-End Flow

### Step 1 — Item added to POS Cart

When a cashier selects an item in the POS:

1. `get_item_detail()` (`pos_next/api/items.py`) fetches the item including `custom_item_category`.
2. The API checks `Item Category.generate_auto_purchase_reciept` and returns `requires_insurance_sr_no: true/false` on the item object.
3. If `requires_insurance_sr_no` was not prefetched, `POSSale.vue` calls `check_insurance_serial_required` as a fallback:
   - **API:** `pos_next.api.items.check_insurance_serial_required`
   - **Params:** `{ item_code }`
   - **Returns:** `{ requires_insurance_sr_no: bool, custom_item_category: str }`

### Step 2 — Insurance Serial Dialog

If `requires_insurance_sr_no` is `true`:

- POS stores the item as `cartStore.pendingItem` (quantity = 1).
- `uiStore.showInsuranceSerialDialog = true` opens `InsuranceSerialDialog.vue`.
- The dialog shows the item name/code and a barcode-scannable input field.
- On confirmation, validates the input is non-empty and emits `insurance-serial-entered` with:
  ```js
  { insurance_sr_no: string, quantity: 1 }
  ```
- **Important:** This dialog is skipped in **auto-add/barcode-scan mode** (`autoAdd = true`).

### Step 3 — Cart Addition

`handleInsuranceSerialEntered()` in `POSSale.vue`:
- Creates the item object with `custom_insurance_sr_no` set.
- Calls `cartStore.addItem()`.

Cart / `useInvoice.js` rules for insurance items:
- **Quantity locked to 1** — the UI shows a locked badge instead of a qty editor.
- **Never merged** — even if the same item code is already in the cart, an insurance item always becomes its own separate line (because each has a unique serial number).

### Step 4 — Save (update_invoice)

When the invoice is saved (`update_invoice`), each item is serialized with:
```python
custom_insurance_sr_no: item.custom_insurance_sr_no or None
allow_zero_valuation_rate: 1  # Insurance items have zero stock valuation
```

### Step 5 — Submit (submit_invoice → before_submit hook)

Before the Sales Invoice is submitted, the `auto_insurance` app fires:

**Hook:** `auto_insurance/hooks.py`
```python
doc_events = {
    "Sales Invoice": {
        "before_submit": "auto_insurance.insurance_auto_pr.create_insurance_purchase_receipt"
    }
}
```

**`create_insurance_purchase_receipt(doc, method=None)`** (`auto_insurance/insurance_auto_pr.py`):

For each item in the Sales Invoice:
1. Reads `Item.custom_item_category`.
2. Checks `Item Category.generate_auto_purchase_reciept` — skips item if not set.
3. Reads `Item Category.category_supplier` — **throws** if not set.
4. Validates `item.custom_insurance_sr_no` is present — **throws** if missing.
5. Calls `create_pr_for_item()`.

**`create_pr_for_item()`**:
1. Creates a new `Purchase Receipt` with:
   - `supplier` = `category_supplier`
   - `posting_date` / `posting_time` = from Sales Invoice
   - `branch` = from Sales Invoice
   - `custom_invoice_attachment` = `/files/auto-pr-placeholder.txt` (placeholder)
2. Adds one item row:
   - `item_code`, `item_name`, `qty`, `uom`, `stock_uom`, `conversion_factor` from the SI item
   - `rate` = fetched from **Standard Buying** price list (`Item Price` where `price_list = "Standard Buying"`)
   - `warehouse`, `branch` from the SI item
3. Calls `set_missing_values()` and `calculate_taxes_and_totals()`.
4. Inserts the PR (`ignore_permissions=True`).
5. **Renames** the PR to the insurance serial number (e.g., `INS-SN-001`).
   - If a PR with that name already exists, appends a counter: `INS-SN-001-1`, `INS-SN-001-2`, etc.
6. Reloads and **submits** the PR.
7. Shows a green alert: `"Purchase Receipt {name} created and submitted for {item_name}"`.

---

## UI Components

### `InsuranceSerialDialog.vue`
`POS/src/components/sale/InsuranceSerialDialog.vue`

- Props: `modelValue` (v-model open/close), `item` (Object), `quantity` (Number, default 1)
- Emits: `insurance-serial-entered` → `{ insurance_sr_no: string, quantity: number }`
- Has error state for empty input.
- Auto-focuses the input field on open for fast barcode scanning.

### `EditItemDialog.vue`
`POS/src/components/sale/EditItemDialog.vue`

- Contains an editable field for `custom_insurance_sr_no` when editing an existing cart line.
- Initialises from `newItem.custom_insurance_sr_no` on open.
- Saves back `updatedItem.custom_insurance_sr_no = localInsuranceSerialNo.value.trim() || null`.

### `InvoiceCart.vue`
`POS/src/components/sale/InvoiceCart.vue`

- For items where `requires_insurance_sr_no` is true or `custom_insurance_sr_no` is set:
  - Replaces the quantity editor with a **locked "qty 1" badge**.
  - Shows a **green insurance badge** (checkmark icon) when the serial has been entered.

### `InvoiceDetailDialog.vue`
`POS/src/components/invoices/InvoiceDetailDialog.vue`

- Displays `custom_insurance_sr_no` on each item row with a green checkmark in both mobile and desktop views.

---

## State Management

### `posUI.js` store
- `showInsuranceSerialDialog` — controls visibility of `InsuranceSerialDialog`.
- Closed (`false`) after the serial is confirmed.

### `posCart.js` store
- `pendingItem` — holds the item awaiting insurance serial entry.
- `pendingItemQty` — quantity (always 1 for insurance items).
- `setPendingItem()` / `clearPendingItem()` — used to park and clear the pending item during the dialog flow.

---

## Key Constraints

| Constraint | Where Enforced |
|---|---|
| Quantity must be 1 | `useInvoice.js` — `isInsuranceSerialItem` check prevents merging; cart badge locks qty |
| No cart merging | `useInvoice.js` — insurance items always get a new cart line |
| Serial is mandatory | `InsuranceSerialDialog.vue` client-side + `insurance_auto_pr.py` server-side |
| category_supplier must be set | `insurance_auto_pr.py` throws before creating PR |
| auto-add / barcode bypass | `POSSale.vue` — `autoAdd` mode skips insurance check |
| `allow_zero_valuation_rate = 1` | `useInvoice.js` serialization — insurance items have no stock valuation |
| PR rate from Standard Buying | `insurance_auto_pr.py` uses `Item Price` with `price_list = "Standard Buying"` |

---

## Error Scenarios

| Scenario | Where | Message |
|---|---|---|
| Empty serial number entered | `InsuranceSerialDialog.vue` | "Insurance Serial Number is required." |
| `category_supplier` not set on Item Category | `insurance_auto_pr.py` | "Category Supplier not set for Item Category: {name}" |
| `custom_insurance_sr_no` missing on SI item | `insurance_auto_pr.py` | "Insurance Serial No is mandatory for item: {item_name}" |
| Duplicate PR name | `insurance_auto_pr.py` | Auto-handled by appending counter to name |

---

## File Reference

| File | Role |
|---|---|
| `pos_next/api/items.py` | `get_item_detail()` — returns `requires_insurance_sr_no`; `check_insurance_serial_required()` — fallback API |
| `POS/src/pages/POSSale.vue` | Orchestrates insurance dialog flow; `handleInsuranceSerialEntered()` |
| `POS/src/components/sale/InsuranceSerialDialog.vue` | Modal for serial number capture |
| `POS/src/components/sale/EditItemDialog.vue` | Edit serial number on existing cart line |
| `POS/src/components/sale/InvoiceCart.vue` | Locked qty badge + insurance badge display |
| `POS/src/components/invoices/InvoiceDetailDialog.vue` | Display serial in invoice detail view |
| `POS/src/composables/useInvoice.js` | No-merge logic + item serialization with `custom_insurance_sr_no` |
| `POS/src/stores/posUI.js` | `showInsuranceSerialDialog` state |
| `auto_insurance/insurance_auto_pr.py` | `create_insurance_purchase_receipt()` — before_submit hook |
| `auto_insurance/hooks.py` | Registers `before_submit` hook on Sales Invoice |
