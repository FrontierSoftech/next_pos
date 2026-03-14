# Copyright (c) 2025, BrainWise and contributors
# For license information, please see license.txt

"""
Sales Invoice Hooks
Event handlers for Sales Invoice document events
"""

import frappe
from frappe import _
from frappe.utils import flt


def validate(doc, method=None):
	"""
	Validate hook for Sales Invoice.
	1. Always correct place_of_supply from billing_address_gstin (for ALL invoices).
	   IC's validate_transaction only validates an existing POS but never recalculates it,
	   so a stale client-sent value (e.g. company state instead of customer state) is
	   saved as-is.  We fix this by recomputing before IC's validation runs.
	2. Apply tax-inclusive settings (POS invoices only).
	3. Adjust paid_amount for finance-lender payments (POS invoices only).

	Args:
		doc: Sales Invoice document
		method: Hook method name (unused)
	"""
	# --- Fix place_of_supply for ALL Sales Invoices ---
	# IC's _validate_links() already re-fetches billing_address_gstin from the address DB
	# before validate runs, so doc.billing_address_gstin is always correct here.
	# We compute the correct place_of_supply and set it if it differs.
	try:
		from india_compliance.gst_india.utils import get_place_of_supply as ic_get_pos
		correct_pos = ic_get_pos(doc, doc.doctype)
		if correct_pos and correct_pos != doc.place_of_supply:
			doc.place_of_supply = correct_pos
	except Exception:
		pass

	if not doc.pos_profile:
		return

	from pos_next.api.tax_utils import apply_tax_inclusive_settings, calculate_taxes_if_needed

	# Apply tax-inclusive settings (filters RCM, sets included_in_print_rate, ensures item amounts)
	if apply_tax_inclusive_settings(doc):
		# Calculate taxes if tax-inclusive mode is active
		calculate_taxes_if_needed(doc, force=True)

		# Warn if taxes are still 0 after calculation
		if doc.get("taxes"):
			total_tax = sum(flt(tax.tax_amount or 0) for tax in doc.get("taxes", []))
			if total_tax == 0:
				frappe.log_error(
					f"WARNING: Tax-inclusive mode but tax amount is 0 after calculation. "
					f"Invoice: {doc.name if hasattr(doc, 'name') else 'NEW'}",
					"POS Tax Inclusive Warning"
				)

	# Adjust paid_amount to include finance lender payments
	# ERPNext's calculate_paid_amount() (called during validate via calculate_taxes_and_totals)
	# and set_paid_amount() (called in SalesInvoice.before_save) only sum the `payments` child
	# table. Finance lender payments are in a custom child table and must be added manually.
	# This runs in validate hook (after class validate) to cover both save and submit flows.
	finance_lender_rows = doc.get("custom_finance_lender_payments", [])
	if finance_lender_rows:
		finance_lender_total = sum(flt(row.amount) for row in finance_lender_rows)
		if finance_lender_total > 0:
			doc.paid_amount = flt(doc.paid_amount) + finance_lender_total
			doc.base_paid_amount = flt(doc.paid_amount * flt(doc.conversion_rate or 1))


def before_save(doc, method=None):
	"""
	Before Save hook for Sales Invoice.
	This runs AFTER validate() and ensures taxes are calculated correctly.
	
	This is critical because set_missing_values() might be called during save,
	which could reload taxes from template and reset included_in_print_rate.
	
	This is the FINAL opportunity to set taxes correctly before save.
	
	Args:
		doc: Sales Invoice document
		method: Hook method name (unused)
	"""
	if not doc.pos_profile:
		return
	
	from pos_next.api.tax_utils import apply_tax_inclusive_settings, calculate_taxes_if_needed
	
	# Apply tax-inclusive settings (filters RCM, sets included_in_print_rate, ensures item amounts)
	# This is the final safeguard before save
	if apply_tax_inclusive_settings(doc):
		# Calculate taxes if tax-inclusive mode is active
		calculate_taxes_if_needed(doc, force=True)
		
		# Final check - if taxes are still 0, log error
		if doc.get("taxes"):
			total_tax = sum(flt(tax.tax_amount or 0) for tax in doc.get("taxes", []))
			if total_tax == 0:
				frappe.log_error(
					f"ERROR: Tax-inclusive mode but tax amount is 0 after calculation! "
					f"Invoice: {doc.name if hasattr(doc, 'name') else 'NEW'}",
					"POS Tax Calculation Error"
				)
	
	# Adjust paid_amount to include finance lender payments (again after before_save)
	# SalesInvoice.before_save() calls set_paid_amount() which resets paid_amount
	# to only sum the `payments` child table. We must re-add finance lender totals.
	finance_lender_rows = doc.get("custom_finance_lender_payments", [])
	if finance_lender_rows:
		finance_lender_total = sum(flt(row.amount) for row in finance_lender_rows)
		if finance_lender_total > 0:
			doc.paid_amount = flt(doc.paid_amount) + finance_lender_total
			doc.base_paid_amount = flt(doc.paid_amount * flt(doc.conversion_rate or 1))


def before_submit(doc, method=None):
	"""
	Before Submit hook for Sales Invoice.
	This hook runs BEFORE the class's before_submit() method which calls add_remarks().
	
	The add_remarks() method only sets remarks if it's empty/None (checks `if not self.remarks:`).
	So if remarks is already set from POS, it will be preserved automatically.
	We don't need to do anything here - just ensure remarks is set before this hook runs.

	Args:
		doc: Sales Invoice document
		method: Hook method name (unused)
	"""
	# No action needed - add_remarks() will preserve existing remarks
	pass


def on_submit(doc, method=None):
	"""
	On Submit hook for Sales Invoice.
	This runs AFTER the document is successfully submitted.
	No action needed for remarks - they should already be preserved.

	Args:
		doc: Sales Invoice document
		method: Hook method name (unused)
	"""
	# No action needed - remarks should already be preserved
	pass


def before_cancel(doc, method=None):
	"""
	Before Cancel hook for Sales Invoice.
	Cancel any credit redemption journal entries.

	Args:
		doc: Sales Invoice document
		method: Hook method name (unused)
	"""
	try:
		from pos_next.api.credit_sales import cancel_credit_journal_entries
		cancel_credit_journal_entries(doc.name)
	except Exception as e:
		frappe.log_error(
			title="Credit Sale JE Cancellation Error",
			message=f"Invoice: {doc.name}, Error: {str(e)}\n{frappe.get_traceback()}"
		)
		# Don't block invoice cancellation if JE cancellation fails
		frappe.msgprint(
			_("Warning: Some credit journal entries may not have been cancelled. Please check manually."),
			alert=True,
			indicator="orange"
		)
