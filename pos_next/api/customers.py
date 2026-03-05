"""
POS Next Customer API
Handles customer search, creation, and management for POS operations
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_customers(search_term="", pos_profile=None, limit=20):

    """
    Search customers for inline customer selection in POS.

    Args:
        search_term (str): Search query (name, mobile, or customer ID)
        pos_profile (str): POS Profile to filter by customer group
        limit (int): Maximum number of results to return

    Returns:
        list: List of customer dictionaries with name, customer_name, mobile_no, email_id
    """
    try:
        frappe.logger().debug(
            f"get_customers called with search_term={search_term}, pos_profile={pos_profile}, limit={limit}"
        )

        filters = {}

        # Filter by POS Profile customer group if specified
        if pos_profile:
            frappe.logger().debug(f"Loading POS Profile: {pos_profile}")
            profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
            # Check if customer_group field exists (it may not exist in all versions)
            if hasattr(profile_doc, "customer_group") and profile_doc.customer_group:
                filters["customer_group"] = profile_doc.customer_group
                frappe.logger().debug(f"Filtering by customer_group: {profile_doc.customer_group}")

        # Only show customers whose customer group has custom_show_in_pos = 1
        # If the custom field doesn't exist, return all customer groups
        pos_groups = []
        try:
            pos_groups = frappe.get_all(
                "Customer Group",
                filters={"custom_show_in_pos": 1},
                pluck="name",
            )
        except Exception as e:
            # custom_show_in_pos field doesn't exist, fallback to all groups
            # This can be frappe.db.ProgrammingError, MySQLdb.OperationalError, etc.
            frappe.logger().debug(f"custom_show_in_pos field not found ({str(e)}), using all customer groups")
            try:
                pos_groups = frappe.get_all(
                    "Customer Group",
                    pluck="name",
                )
            except Exception as fallback_e:
                frappe.logger().warning(f"Could not fetch customer groups: {str(fallback_e)}")
                pos_groups = []
        
        if pos_groups:
            filters["customer_group"] = ["in", pos_groups]
        else:
            # No groups found — return all customers without group filter
            frappe.logger().debug("No customer groups found, returning all customers")

        # Return all customers (for client-side filtering)
        filters["disabled"] = 0
        customer_limit = limit if limit not in (None, 0) else frappe.db.count("Customer", filters)
        result = frappe.get_all(
            "Customer",
            filters=filters,
            fields=["name", "customer_name", "mobile_no", "email_id", "custom_party_name_for_print", "customer_group", "custom_profession", "gstin", "gst_category", "customer_type"],
            limit=customer_limit,
            order_by="customer_name asc",
        )
        frappe.logger().debug(f"get_customers returned {len(result)} customers")
        return result
    except Exception as e:
        frappe.logger().error(f"Error in get_customers: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        frappe.throw(_("Error fetching customers: {0}").format(str(e)))


@frappe.whitelist()
def create_customer(customer_name, mobile_no=None, email_id=None, customer_group="Individual", territory="All Territories"):
    """
    Create a new customer from POS.

    Args:
        customer_name (str): Customer name (required)
        mobile_no (str): Mobile number (optional)
        email_id (str): Email address (optional)
        customer_group (str): Customer group (default: Individual)
        territory (str): Territory (default: All Territories)

    Returns:
        dict: Created customer document
    """
    # Check if user has permission to create customers
    if not frappe.has_permission("Customer", "create"):
        frappe.throw(_("You don't have permission to create customers"), frappe.PermissionError)

    if not customer_name:
        frappe.throw(_("Customer name is required"))

    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": "Individual",
            "customer_group": customer_group or "Individual",
            "territory": territory or "All Territories",
            "mobile_no": mobile_no or "",
            "email_id": email_id or "",
        }
    )

    customer.insert()

    return customer.as_dict()


@frappe.whitelist()
def get_customer_details(customer):
    """
    Get detailed customer information.

    Args:
        customer (str): Customer ID

    Returns:
        dict: Customer details
    """
    if not customer:
        frappe.throw(_("Customer is required"))

    return frappe.get_cached_doc("Customer", customer).as_dict()


@frappe.whitelist()
def update_customer(customer_name, updates):
    """
    Update customer fields from POS, including email via linked Contact.

    Args:
        customer_name (str): Customer document name
        updates (dict): Fields to update on the Customer doc
                        Special key 'email_id' updates the linked Contact

    Returns:
        dict: Updated customer fields
    """
    if not frappe.has_permission("Customer", "write"):
        frappe.throw(_("You don't have permission to edit customers"), frappe.PermissionError)

    if not customer_name:
        frappe.throw(_("Customer name is required"))

    if isinstance(updates, str):
        import json
        updates = json.loads(updates)

    customer = frappe.get_doc("Customer", customer_name)

    # Extract email_id — needs to go to Contact, not Customer directly
    new_email = updates.pop("email_id", None)

    # Update direct Customer fields
    for field, value in updates.items():
        if hasattr(customer, field):
            setattr(customer, field, value)

    customer.save()

    # Update email via linked Contact
    if new_email:
        contacts = frappe.get_all(
            "Contact",
            filters=[
                ["Dynamic Link", "link_doctype", "=", "Customer"],
                ["Dynamic Link", "link_name", "=", customer_name],
            ],
            fields=["name"],
            limit=1,
        )
        if contacts:
            contact = frappe.get_doc("Contact", contacts[0].name)
            if contact.email_ids:
                contact.email_ids[0].email_id = new_email
            else:
                contact.append("email_ids", {"email_id": new_email, "is_primary": 1})
            contact.save()

    # Return fresh customer data with email_id
    result = frappe.get_value(
        "Customer",
        customer_name,
        ["name", "customer_name", "mobile_no", "email_id", "custom_party_name_for_print",
         "customer_group", "custom_profession", "gstin", "gst_category", "customer_type"],
        as_dict=True,
    )
    return result


@frappe.whitelist()
def get_profession_options():
    """
    Get profession options from Custom Field without requiring Custom Field permissions.

    Returns:
        list: List of profession options
    """
    try:
        # Query the custom field options directly from database
        # This bypasses permission checks on Custom Field doctype
        options = frappe.db.get_value(
            "Custom Field",
            {
                "dt": "Customer",
                "fieldname": "custom_profession"
            },
            "options"
        )

        if options:
            # Split by newline and filter empty strings
            profession_list = [p.strip() for p in options.split("\n") if p.strip()]
            return profession_list
        else:
            # Return default professions if custom field not found
            return ["Doctor", "Accountant", "Business", "CA", "Student"]

    except Exception as e:
        frappe.log_error(f"Error fetching profession options: {str(e)}", "Get Profession Options Error")
        # Return default professions on error
        return ["Doctor", "Accountant", "Business", "CA", "Student"]
