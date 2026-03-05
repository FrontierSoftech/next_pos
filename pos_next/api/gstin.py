"""
API endpoints for GSTIN verification and autofill in POS
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_gstin_info_for_pos(gstin):
	"""
	Fetch GSTIN information for POS customer creation.
	Calls India Compliance's internal _get_gstin_info (bypasses desk-access check
	so POS users without desk access can still use the feature).

	Requires: GST Settings → Enable API → set API Secret from indiacompliance.app

	Returns dict with keys:
	  business_name, gst_category, status,
	  permanent_address: { line1, line2, city, state, pincode, country }
	"""
	try:
		from india_compliance.gst_india.utils import validate_gstin
		from india_compliance.gst_india.utils.gstin_info import _get_gstin_info

		gstin = validate_gstin(gstin)

		# throw_error=False silently returns empty dict on any failure (e.g. API not configured).
		gstin_info = _get_gstin_info(gstin, doc=frappe._dict({"doctype": "Customer"}), throw_error=False)

		if not gstin_info or not gstin_info.get("business_name"):
			# Distinguish between "API not set up" and "GSTIN not found" for a clear message.
			from india_compliance.gst_india.utils import can_enable_api
			settings = frappe.get_cached_doc("GST Settings")
			if not settings.enable_api or not can_enable_api(settings):
				return {
					"error": True,
					"message": _(
						"India Compliance API is not configured. "
						"Go to GST Settings → enable API → enter the API Secret "
						"from your indiacompliance.app account to enable GSTIN autofill."
					),
				}
			return {
				"error": True,
				"message": _("No data found for this GSTIN. Please verify the number and try again."),
			}

		# India Compliance returns address fields as address_line1 / address_line2,
		# but the POS dialog reads line1 / line2 — remap before returning.
		if gstin_info.get("permanent_address"):
			addr = gstin_info["permanent_address"]
			gstin_info["permanent_address"] = {
				"line1":    addr.get("address_line1", ""),
				"line2":    addr.get("address_line2", ""),
				"city":     addr.get("city", ""),
				"state":    addr.get("state", ""),
				"pincode":  addr.get("pincode", ""),
				"country":  addr.get("country", "India"),
			}

		return gstin_info

	except Exception as e:
		error_msg = str(e)
		frappe.log_error(
			title="POS GSTIN Verification Error",
			message=f"GSTIN: {gstin}\n{error_msg}"
		)

		if "check digit" in error_msg.lower():
			error_msg = _("Invalid GSTIN. The check digit validation failed — please re-enter and try again.")
		elif "not allowed" in error_msg.lower() or "permission" in error_msg.lower():
			error_msg = _("Permission denied. Please contact your system administrator.")

		return {"error": True, "message": error_msg}


@frappe.whitelist()
def check_duplicate_gstin_for_pos(gstin):
	"""
	Check if a GSTIN is already registered with an existing Customer.
	POS-safe: no desk-access check, read-only DB query.

	Returns dict:
	  { exists: bool, customer: str|None, customer_name: str|None }
	"""
	if not gstin:
		return {"exists": False}

	gstin = gstin.upper().strip()

	existing = frappe.db.get_value(
		"Customer",
		{"gstin": gstin, "disabled": 0},
		["name", "customer_name"],
		as_dict=True,
	)

	if existing:
		return {
			"exists": True,
			"customer": existing.name,
			"customer_name": existing.customer_name,
		}

	return {"exists": False}
