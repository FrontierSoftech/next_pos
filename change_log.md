# POS Next – Change Log

---

## [Unreleased] – 2026-03-05

### POS Closing Shift – Item Group Sales & Finance Lender Payments (DB persistence)

**Files changed:**
- `pos_next/pos_next/doctype/pos_closing_shift/pos_closing_shift.json` – Added two new Table fields: `item_group_sales` (→ POS Closing Shift Item Group) and `finance_lender_payments` (→ POS Closing Shift Finance Lender).
- `pos_next/pos_next/doctype/pos_closing_shift_item_group/` (new) – Child doctype with fields: `item_group` (Data), `qty` (Float), `amount` (Currency).
- `pos_next/pos_next/doctype/pos_closing_shift_finance_lender/` (new) – Child doctype with fields: `finance_lender` (Data), `mode` (Data), `amount` (Currency).

**Behaviour:** When a POS Closing Shift is submitted, item-group-wise sales totals and finance lender payment totals collected during the shift are now saved as child table rows on the POS Closing Shift document (in addition to being displayed in the UI). Requires `bench migrate` after deployment.

---

### POS Closing Shift – UI Redesign (Shift Summary)

**Commit:** _unreleased (same batch as above)_

**Files changed:**
- `POS/src/components/ShiftClosingDialog.vue` – Replaced previous summary with two new collapsible sections:
  1. **Sales by Item Group** – table showing Item Group / Qty / Amount with totals footer.
  2. **Finance Lender Payments** – table showing Finance Lender / Mode / Amount with totals footer.
- `pos_next/api/shifts.py` – Added `_get_item_group_sales()` and `_get_finance_lender_payments()` helper functions. Both query submitted Sales Invoices linked to the opening shift via `posa_pos_opening_shift`. Results are appended to the closing shift data returned by `get_closing_shift_data()`.

---

### GSTIN Autofill in POS

**Commit:** _unreleased_

**Files changed:**
- `pos_next/api/gstin.py` – Rewrote to call India Compliance's internal `_get_gstin_info()` (bypasses desk-access check for POS users). Detects unconfigured API key and returns a clear user message. Remaps `address_line1`/`address_line2` → `line1`/`line2` to match the frontend dialog's expected keys.

**Prerequisite:** India Compliance app installed + GST Settings → Enable API → API Secret configured from indiacompliance.app.

---

## [f5a7f90] – POS Offers, Badge Count, UOM Dialog, Custom Alias Barcode

### POS Offer Apply Support

**Files changed:**
- `pos_next/api/invoices.py` – `apply_offers()`: Added handling for `tabPOS Offer` records (separate from ERPNext Pricing Rules). Manually applies item/item-group/brand discounts for POS Offers before the ERPNext pricing engine runs.

### Offers Badge Count Fix

**Files changed:**
- `POS/src/components/sale/InvoiceCart.vue` – Badge now shows `allEligibleOffers.length` instead of `autoEligibleCount`, so all eligible offers (not just auto-apply ones) are reflected in the badge.

### UOM Dialog Fix – Non-Serialised Items

**Files changed:**
- `POS/src/pages/POSSale.vue` – UOM selection popup now only shown when `item.item_uoms.length > 1`. Previously showed even for single-UOM items, blocking direct cart addition on barcode scan / Enter key.

### Custom Alias Barcode Scan

**Files changed:**
- `pos_next/api/items.py` – `search_by_barcode()`: Added lookup on `custom_alias` field of Item doctype after the standard item-code lookup, before Serial No lookup.

---

## [5f4c5a1] – fetch POS Offer records in get_offers API

**Files changed:**
- `pos_next/api/offers.py` – `get_offers()`: Added `_get_pos_offer_records()` which queries `tabPOS Offer` directly. Previously only Pricing Rules from ERPNext were returned, making POS Offer records invisible in the Available Offers modal.

---

## [d4eb279] – Fix: discount not applying to duplicate insurance cart items

**Files changed:**
- `pos_next/api/invoices.py` – Fixed edge case where duplicate items (same item, different insurance) would not receive discounts correctly.

---

## [f9b368e] – Handle non-GST customers with branch place_of_supply; GST tax detection improvements

**Files changed:**
- `pos_next/api/gst_tax.py` – Normal customers (no GSTIN / Unregistered) always treated as intrastate → CGST+SGST. Company state used as fallback in `get_place_of_supply()`.
- `pos_next/api/customers.py` – `get_customer_addresses()` now returns `custom_branch` and `custom_place_of_supply`.
- Various Internal Transfer Mode fixes (see `memory/internal_transfer.md`).

---

## [38104ce] – Initial commit: pos_next app
