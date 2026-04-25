# -*- coding: utf-8 -*-
# Copyright (c) 2025, BrainWise and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


@frappe.whitelist()
def search_accounts(search_term="", company=None, limit=20):
	"""
	Search for Bank/Cash accounts for Finance Lender selection.

	Args:
	    search_term: Search string to filter accounts
	    company: Company to filter accounts by
	    limit: Maximum number of results to return

	Returns:
	    List of account dictionaries with name and account_type
	"""
	# Use parameterized queries for safety
	conditions = ["account_type IN ('Bank', 'Cash')", "is_group = 0"]
	params = {}

	if company:
		conditions.append("company = %(company)s")
		params["company"] = company

	if search_term:
		conditions.append("(name LIKE %(search_pattern)s OR account_name LIKE %(search_pattern)s)")
		params["search_pattern"] = f"%{search_term}%"

	where_clause = " AND ".join(conditions)

	# Query accounts
	accounts = frappe.db.sql(
		f"""
        SELECT
            name,
            account_name,
            account_type
        FROM `tabAccount`
        WHERE {where_clause}
        ORDER BY name
        LIMIT %(limit)s
        """,
		{**params, "limit": int(limit)},
		as_dict=True,
	)

	return accounts


@frappe.whitelist()
def search_finance_lenders(search_term="", pos_profile=None, limit=20):
	"""
	Search for customers in the 'Finance Lender' customer group (including descendants),
	filtered by the POS Profile's branch.

	Args:
	    search_term: Search string to filter customers
	    pos_profile: POS Profile name to determine branch filter
	    limit: Maximum number of results to return

	Returns:
	    List of customer dictionaries with name and customer_name
	"""
	conditions = []
	params = {}

	# Get all customer groups under 'Finance Lender' (descendants)
	# First get direct children of Finance Lender
	finance_lender_groups = frappe.get_all(
		"Customer Group",
		filters={"parent_customer_group": "Finance Lender"},
		pluck="name",
	)
	# Add the parent group itself
	finance_lender_groups = finance_lender_groups + ["Finance Lender"]

	# Also get grandchildren (children of children)
	def get_all_descendants(parent_group, depth=3):
		"""Recursively get all descendants up to a certain depth"""
		children = frappe.get_all(
			"Customer Group",
			filters={"parent_customer_group": parent_group},
			pluck="name",
		)
		all_children = list(children)
		if depth > 0:
			for child in children:
				all_children.extend(get_all_descendants(child, depth - 1))
		return all_children

	# Get all descendants up to 3 levels deep
	all_descendants = get_all_descendants("Finance Lender", depth=3)
	finance_lender_groups.extend(all_descendants)

	# Remove duplicates
	finance_lender_groups = list(set(finance_lender_groups))

	if finance_lender_groups:
		conditions.append("customer_group IN %(finance_lender_groups)s")
		params["finance_lender_groups"] = finance_lender_groups
	else:
		# Fallback to exact match if no descendants found
		conditions.append("customer_group = 'Finance Lender'")

	# Filter by branch matching the POS Profile's branch
	if pos_profile:
		branch = frappe.db.get_value("POS Profile", pos_profile, "branch")
		if branch:
			conditions.append("custom_branch = %(branch)s")
			params["branch"] = branch

	if search_term:
		conditions.append("(name LIKE %(search_pattern)s OR customer_name LIKE %(search_pattern)s)")
		params["search_pattern"] = f"%{search_term}%"

	conditions.append("disabled = 0")

	where_clause = " AND ".join(conditions)

	customers = frappe.db.sql(
		f"""
        SELECT
            name,
            customer_name
        FROM `tabCustomer`
        WHERE {where_clause}
        ORDER BY customer_name
        LIMIT %(limit)s
        """,
		{**params, "limit": int(limit)},
		as_dict=True,
	)

	return customers
