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
        as_dict=True
    )

    return accounts


@frappe.whitelist()
def search_finance_lenders(search_term="", pos_profile=None, limit=20):
    """
    Search for customers in the 'Finance Lender' customer group,
    filtered by the POS Profile's branch.

    Args:
        search_term: Search string to filter customers
        pos_profile: POS Profile name to determine branch filter
        limit: Maximum number of results to return

    Returns:
        List of customer dictionaries with name and customer_name
    """
    conditions = ["customer_group = 'Finance Lender'"]
    params = {}

    # Filter by branch matching the POS Profile's branch
    if pos_profile:
        branch = frappe.db.get_value("POS Profile", pos_profile, "branch")
        if branch:
            conditions.append("custom_branch = %(branch)s")
            params["branch"] = branch

    if search_term:
        conditions.append("(name LIKE %(search_pattern)s OR customer_name LIKE %(search_pattern)s)")
        params["search_pattern"] = f"%{search_term}%"

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
        as_dict=True
    )

    return customers
