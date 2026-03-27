# POS Next – Deployment Guide

This file tracks all steps required on the cloud/production server when deploying updates.

---

## Deploy: 2026-03-05 – Closing Shift Child Doctypes + GSTIN Autofill + Offer/UOM Fixes

### Pull the latest code

```bash
cd /home/frappe/frappe-bench
bench get-app pos_next https://github.com/<your-org>/pos_next  # or: git -C apps/pos_next pull
```

Or if using a private remote:

```bash
git -C apps/pos_next pull origin master
```

### Run migration (REQUIRED)

Two new child doctypes were added to POS Closing Shift (`POS Closing Shift Item Group` and `POS Closing Shift Finance Lender`). The database tables must be created before the app is usable.

```bash
bench --site <your-site> migrate
```

### Rebuild frontend assets

```bash
bench build --app pos_next
```

Or if using a production build pipeline, trigger the frontend build and ensure the new `ShiftClosingDialog.vue` output is deployed.

### Restart services

```bash
bench restart
# or in production with supervisor:
sudo supervisorctl restart all
```

### Verify

1. Open a POS session and close a shift.
2. In the Close POS Shift dialog, confirm:
   - "Sales by Item Group" section shows item-group breakdown.
   - "Finance Lender Payments" section shows lender-wise totals (if applicable).
3. After submitting the shift, open the resulting **POS Closing Shift** document in ERPNext and confirm the two child tables are populated.

---

## One-time Setup: GSTIN Autofill (India Compliance)

Requires India Compliance app to be installed and configured.

1. Go to **GST Settings** in ERPNext.
2. Enable **API**.
3. Paste the **API Secret** from your [indiacompliance.app](https://indiacompliance.app) account.
4. Save.

Once configured, the POS customer creation dialog will auto-fill business name and address from GSTIN.

---

## Previous Deployments

### [f5a7f90] – POS Offers, Badge Count, UOM Dialog, Custom Alias Barcode

**Steps required:**
- `git pull` + `bench build --app pos_next` + `bench restart`
- No migration needed (no schema changes).

**Custom field prerequisite:**
- Ensure `custom_alias` field exists on the **Item** doctype (Data, searchable). If not present, create it via **Customize Form → Item**.

### [5f4c5a1] – fetch POS Offer records in get_offers API

**Steps required:**
- `git pull` + `bench restart`
- No migration or build needed (backend-only change).

### [f9b368e] – GST tax detection / non-GST customer fix

**Steps required:**
- `git pull` + `bench restart`
- No migration needed.
- Confirm **POS Profile → Company Address** has the correct `gst_state_number` and `gstin` set for Internal Transfer mode to work correctly.

---

## Recurring Deployment Checklist

| Step | Command | When needed |
|------|---------|-------------|
| Pull code | `git -C apps/pos_next pull` | Every deploy |
| Migrate DB | `bench --site <site> migrate` | When `*.json` DocType files changed |
| Build frontend | `bench build --app pos_next` | When `POS/src/**` Vue/JS files changed |
| Restart services | `bench restart` | Every deploy |
| Clear cache | `bench --site <site> clear-cache` | If stale data after deploy |
