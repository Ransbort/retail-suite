import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from retail.retail.workspace_installer import workspace_installer, workspace_remover

def setup():
	make_custom_fields()
	workspace_installer()

def uninstall():
	custom_fields = get_custom_fields()
	delete_custom_fields(custom_fields)
	workspace_remover()

def make_custom_fields(update=True):
	custom_fields = get_custom_fields()
	create_custom_fields(custom_fields,update=update)

def delete_custom_fields(custom_fields: dict):
	"""
	:param custom_fields: a dict like `{'Pos Profile': [{fieldname: '', ...}]}`
	"""
	for doctype, fields in custom_fields.items():
		frappe.db.delete(
			"Custom Field",
			{
				"fieldname": ("in", [field["fieldname"] for field in fields]),
				"dt": doctype,
			},
		)

		frappe.clear_cache(doctype=doctype)

def get_custom_fields():
	return {
		"POS Profile": [
			{"fieldname": "posa_store_settings","label": "Store Settings","fieldtype": "Tab Break","insert_after": "utm_medium"},
			{"fieldname": "posa_store_info", "label": "Store Info", "fieldtype": "Section Break", "insert_after": "posa_store_settings"},
			{"fieldname": "posa_store_name", "label": "Store Name", "fieldtype": "Data", "insert_after": "posa_store_info", "reqd": 1},
			{"fieldname": "posa_store_address", "label": "Store Address", "fieldtype": "Link", "insert_after": "posa_store_name", "options": "Address", "reqd": 1},
			{"fieldname": "posa_store_email", "label": "Store Email", "fieldtype": "Data", "insert_after": "posa_store_address", "reqd": 1},
			{"fieldname": "posa_column_break_6uxg7", "fieldtype": "Column Break", "insert_after": "posa_store_email"},
			{"fieldname": "posa_tax_id", "label": "Tax Id", "fieldtype": "Int", "insert_after": "posa_column_break_6uxg7", "reqd": 1},
			{"fieldname": "posa_store_phone", "label": "Store Phone", "fieldtype": "Phone", "insert_after": "posa_tax_id", "reqd": 1},
			{"fieldname": "posa_receipt_info_section", "label": "Receipt Info", "fieldtype": "Section Break", "insert_after": "posa_store_phone"},
			{"fieldname": "posa_show_store_logo", "label": "Show Store Logo", "fieldtype": "Check", "insert_after": "posa_receipt_info_section"},
			{"fieldname": "posa_store_logo", "label": "Store Logo", "fieldtype": "Image", "insert_after": "posa_show_store_logo"},
			{"fieldname": "posa_column_break_eifq", "fieldtype": "Column Break", "insert_after": "posa_store_logo"},
			{"fieldname": "posa_show_thank_you", "label": "Show Thank You", "fieldtype": "Check", "insert_after": "posa_column_break_eifq"},
			{"fieldname": "posa_footer_message", "label": "Footer Message", "fieldtype": "Small Text", "insert_after": "posa_show_thank_you"},
			{"fieldname": "posa_appearance_section", "label": "Appearance", "fieldtype": "Section Break", "insert_after": "posa_footer_message"},
			{"fieldname": "posa_primary_color", "label": "Primary Color", "fieldtype": "Color", "insert_after": "posa_appearance_section"},
			{"fieldname": "posa_column_break_dtmt", "fieldtype": "Column Break", "insert_after": "posa_primary_color"},
			{"fieldname": "posa_theme", "label": "Theme", "fieldtype": "Select", "insert_after": "posa_column_break_dtmt", "options": "\ndark\nlight"},
			{"fieldname": "posa_printer_settings_section", "label": "Printer Settings", "fieldtype": "Section Break", "insert_after": "posa_theme"},
			{"fieldname": "posa_printer_ip", "label": "Printer IP", "fieldtype": "Data", 'reqd': 1, "insert_after": "posa_printer_settings_section"},
			{"fieldname": "posa_printer_port", "label": "Printer Port", "fieldtype": "Int", 'reqd': 1, "insert_after": "posa_printer_ip"},
			{"fieldname": "posa_printer_type", "label": "Printer Type", "fieldtype": "Select", 'reqd': 1, "insert_after": "posa_printer_port", "options": "\nThermal Printer\nLaser Printer\nInkjet Printer"},
			{"fieldname": "posa_column_break_pxom", "fieldtype": "Column Break", "insert_after": "posa_printer_type"},
			{"fieldname": "posa_paper_size", "label": "Paper Size", "fieldtype": "Select", 'reqd': 1, "insert_after": "posa_column_break_pxom", "options": "\n80mm\n58mm\nA4\nA5"},
			{"fieldname": "posa_paper_width", "label": "Paper Width", "fieldtype": "Int", "insert_after": "posa_paper_size"},
			{"fieldname": "posa_paper_height", "label": "Paper Height", "fieldtype": "Int", "insert_after": "posa_paper_width"},
			{"fieldname": "posa_pos_settings_section", "label": "Pos Settings", "fieldtype": "Section Break", "insert_after": "posa_paper_height"},
			{"fieldname": "posa_items_per_page", "label": "Items Per Page", "fieldtype": "Int", "insert_after": "posa_pos_settings_section"},
			{"fieldname": "posa_language", "label": "Language", "fieldtype": "Link", "insert_after": "posa_items_per_page", "options": "Language"},
			{"fieldname": "posa_column_break_lufg", "fieldtype": "Column Break", "insert_after": "posa_language"},
			{"fieldname": "posa_offline_mode", "label": "Offline Mode", "fieldtype": "Check", "insert_after": "posa_column_break_lufg"},
			{"fieldname": "posa_sound_effects", "label": "Sound Effects", "fieldtype": "Check", "insert_after": "posa_offline_mode"},
			# POS Awesome Settings
			{"fieldname": "posa_pos_awesome_settings", "label": "POS Awesome Settings", "fieldtype": "Section Break", "insert_after": "posa_sound_effects", "collapsible": 1},
			{"fieldname": "posa_cash_mode_of_payment", "label": "Cash Mode of Payment", "fieldtype": "Link", "insert_after": "posa_pos_awesome_settings", "options": "Mode of Payment", "description": "For POS Closing Shift Payment Reconciliation"},
			{"fieldname": "posa_allow_delete", "label": "Auto Delete Draft Invoice", "fieldtype": "Check", "insert_after": "posa_cash_mode_of_payment", "default": "0"},
			{"fieldname": "posa_allow_user_to_edit_rate", "label": "Allow user to edit Rate", "fieldtype": "Check", "insert_after": "posa_allow_delete", "default": "0"},
			{"fieldname": "posa_allow_user_to_edit_additional_discount", "label": "Allow user to edit Additional Discount", "fieldtype": "Check", "insert_after": "posa_allow_user_to_edit_rate"},
			{"fieldname": "posa_use_percentage_discount", "label": "Use Percentage Discount", "fieldtype": "Check", "insert_after": "posa_allow_user_to_edit_additional_discount", "depends_on": "posa_allow_user_to_edit_additional_discount", "default": "0"},
			{"fieldname": "posa_max_discount_allowed", "label": "Max Discount Percentage Allowed", "fieldtype": "Float", "insert_after": "posa_use_percentage_discount", "default": "0"},
			{"fieldname": "posa_scale_barcode_start", "label": "Scale Barcode Start With", "fieldtype": "Int", "insert_after": "posa_max_discount_allowed", "default": "221", "description": "It is best not to use more than four numbers"},
			{"fieldname": "posa_allow_change_posting_date", "label": "Allow Change Posting Date", "fieldtype": "Check", "insert_after": "posa_scale_barcode_start"},
			{"fieldname": "posa_default_card_view", "label": "Default Card View", "fieldtype": "Check", "insert_after": "posa_allow_change_posting_date"},
			{"fieldname": "posa_default_sales_order", "label": "Default Sales Order", "fieldtype": "Check", "insert_after": "posa_default_card_view"},
			{"fieldname": "posa_col_1", "fieldtype": "Column Break", "insert_after": "posa_default_sales_order"},
			{"fieldname": "posa_allow_user_to_edit_item_discount", "label": "Allow User to Edit Item Discount", "fieldtype": "Check", "insert_after": "posa_col_1"},
			{"fieldname": "posa_display_items_in_stock", "label": "Hide Unavailable Items", "fieldtype": "Check", "insert_after": "posa_allow_user_to_edit_item_discount", "default": "0"},
			{"fieldname": "posa_allow_partial_payment", "label": "Allow Partial Payment", "fieldtype": "Check", "insert_after": "posa_display_items_in_stock", "default": "0"},
			{"fieldname": "posa_allow_credit_sale", "label": "Allow Credit Sale", "fieldtype": "Check", "insert_after": "posa_allow_partial_payment", "depends_on": "posa_allow_partial_payment", "default": "0"},
			{"fieldname": "posa_allow_return", "label": "Allow Return", "fieldtype": "Check", "insert_after": "posa_allow_credit_sale"},
			{"fieldname": "posa_apply_customer_discount", "label": "Apply Customer Discount", "fieldtype": "Check", "insert_after": "posa_allow_return", "default": "0"},
			{"fieldname": "posa_use_cashback", "label": "Use Cashback", "fieldtype": "Check", "insert_after": "posa_apply_customer_discount", "default": "0"},
			{"fieldname": "posa_hide_closing_shift", "label": "Hide Close Shift", "fieldtype": "Check", "insert_after": "posa_use_cashback"},
			{"fieldname": "posa_auto_set_batch", "label": "Auto Set Batch", "fieldtype": "Check", "insert_after": "posa_hide_closing_shift"},
			{"fieldname": "posa_display_item_code", "label": "Display Item Code", "fieldtype": "Check", "insert_after": "posa_auto_set_batch", "default": "0"},
			{"fieldname": "posa_allow_zero_rated_items", "label": "Allow Zero Rated Items", "fieldtype": "Check", "insert_after": "posa_display_item_code"},
			{"fieldname": "posa_hide_expected_amount", "label": "Hide Expected Amount", "fieldtype": "Check", "insert_after": "posa_allow_zero_rated_items"},
			{"fieldname": "posa_column_break_112", "fieldtype": "Column Break", "insert_after": "posa_hide_expected_amount"},
			{"fieldname": "posa_allow_sales_order", "label": "Allow Create Sales Order", "fieldtype": "Check", "insert_after": "posa_column_break_112"},
			{"fieldname": "posa_show_template_items", "label": "Show Template Items", "fieldtype": "Check", "insert_after": "posa_allow_sales_order"},
			{"fieldname": "posa_hide_variants_items", "label": "Hide Variants Items", "fieldtype": "Check", "insert_after": "posa_show_template_items", "depends_on": "posa_show_template_items"},
			{"fieldname": "posa_fetch_coupon", "label": "Auto Fetch Coupon Gifts", "fieldtype": "Check", "insert_after": "posa_hide_variants_items"},
			{"fieldname": "posa_allow_customer_purchase_order", "label": "Allow Customer Purchase Order", "fieldtype": "Check", "insert_after": "posa_fetch_coupon", "default": "0"},
			{"fieldname": "posa_allow_print_last_invoice", "label": "Allow Print Last Invoice", "fieldtype": "Check", "insert_after": "posa_allow_customer_purchase_order", "default": "0"},
			{"fieldname": "posa_display_additional_notes", "label": "Display Additional Notes", "fieldtype": "Check", "insert_after": "posa_allow_print_last_invoice"},
			{"fieldname": "posa_allow_write_off_change", "label": "Allow Write Off Change", "fieldtype": "Check", "insert_after": "posa_display_additional_notes"},
			{"fieldname": "posa_new_line", "label": "Allow add New Items on New Line", "fieldtype": "Check", "insert_after": "posa_allow_write_off_change", "default": "0"},
			{"fieldname": "posa_input_qty", "label": "Use QTY Input", "fieldtype": "Check", "insert_after": "posa_new_line", "default": "0"},
			{"fieldname": "posa_allow_print_draft_invoices", "label": "Allow Print Draft Invoices", "fieldtype": "Check", "insert_after": "posa_input_qty"},
			{"fieldname": "posa_use_delivery_charges", "label": "Use Delivery Charges", "fieldtype": "Check", "insert_after": "posa_allow_print_draft_invoices"},
			{"fieldname": "posa_auto_set_delivery_charges", "label": "Auto Set Delivery Charges", "fieldtype": "Check", "insert_after": "posa_use_delivery_charges"},
			{"fieldname": "posa_allow_duplicate_customer_names", "label": "Allow Duplicate Customer Names", "fieldtype": "Check", "insert_after": "posa_auto_set_delivery_charges"},
			# Payments
			{"fieldname": "posa_payments", "label": "POS Awesome Payments", "fieldtype": "Section Break", "insert_after": "posa_allow_duplicate_customer_names", "collapsible": 1},
			{"fieldname": "posa_use_pos_awesome_payments", "label": "Use POS Awesome Payments", "fieldtype": "Check", "insert_after": "posa_payments"},
			{"fieldname": "posa_column_break_uolvm", "fieldtype": "Column Break", "insert_after": "posa_use_pos_awesome_payments"},
			{"fieldname": "posa_allow_make_new_payments", "label": "Allow Make New Payments", "fieldtype": "Check", "insert_after": "posa_column_break_uolvm", "depends_on": "posa_use_pos_awesome_payments", "default": "1"},
			{"fieldname": "posa_allow_reconcile_payments", "label": "Allow Reconcile Payments", "fieldtype": "Check", "insert_after": "posa_allow_make_new_payments", "depends_on": "posa_use_pos_awesome_payments", "default": "1"},
			{"fieldname": "posa_allow_mpesa_reconcile_payments", "label": "Allow Mpesa Reconcile Payments", "fieldtype": "Check", "insert_after": "posa_allow_reconcile_payments", "depends_on": "posa_use_pos_awesome_payments"},
			# Advance Settings
			{"fieldname": "posa_pos_awesome_advance_settings", "label": "POS Awesome Advance Settings", "fieldtype": "Section Break", "insert_after": "posa_allow_mpesa_reconcile_payments", "collapsible": 1},
			{"fieldname": "posa_allow_submissions_in_background_job", "label": "Allow Submissions in background job", "fieldtype": "Check", "insert_after": "posa_pos_awesome_advance_settings", "description": "Send invoice to submit after printing"},
			{"fieldname": "posa_search_serial_no", "label": "Search by Serial Number", "fieldtype": "Check", "insert_after": "posa_allow_submissions_in_background_job"},
			{"fieldname": "posa_search_batch_no", "label": "Search by Batch Number", "fieldtype": "Check", "insert_after": "posa_search_serial_no"},
			{"fieldname": "posa_tax_inclusive", "label": "Tax Inclusive", "fieldtype": "Check", "insert_after": "posa_search_batch_no", "default": "1"},
			{"fieldname": "posa_column_break_dqsba", "fieldtype": "Column Break", "insert_after": "posa_tax_inclusive"},
			{"fieldname": "posa_local_storage", "label": "Use Browser Local Storage", "fieldtype": "Check", "insert_after": "posa_column_break_dqsba", "default": "1"},
			{"fieldname": "posa_use_server_cache", "label": "Use Server Cache", "fieldtype": "Check", "insert_after": "posa_local_storage", "default": "0", "description": "Use Redis cache on the server to speedup initial loads of POS Awesome"},
			{"fieldname": "posa_server_cache_duration", "label": "Server Cache Duration", "fieldtype": "Int", "insert_after": "posa_use_server_cache", "depends_on": "posa_use_server_cache", "default": "30", "description": "Cache the values for n minutes", "non_negative": 1},
			{"fieldname": "posa_column_break_anyol", "fieldtype": "Column Break", "insert_after": "posa_server_cache_duration"},
			{"fieldname": "posa_search_limit", "label": "Search Limit Number", "fieldtype": "Int", "insert_after": "posa_column_break_anyol", "depends_on": "posa_use_limit_search", "mandatory_depends_on": "posa_use_limit_search", "default": "500", "description": "Search Limit for Items\nFor best performance keep this under 1500", "non_negative": 1},
			{"fieldname": "posa_use_limit_search", "label": "Use Limit Search", "fieldtype": "Check", "insert_after": "posa_search_limit", "description": "Use Search Limit for Items"},
			{"fieldname": "posa_use_customer_credit", "label": "Use Customer Credit", "fieldtype": "Check", "insert_after": "posa_use_limit_search", "default": "0"},
		],
		"Sales Invoice":[
		{'fieldname': 'posa_delivery_date', 'label': 'Delivery Date', 'fieldtype': 'Date', 'insert_after': 'posa_column_break_111', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_column_break_111', 'label': '', 'fieldtype': 'Column Break', 'insert_after': 'posa_notes', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_notes', 'label': 'Additional Notes', 'fieldtype': 'Small Text', 'insert_after': 'posa_additional_notes_section', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_additional_notes_section', 'label': 'Additional Notes', 'fieldtype': 'Section Break', 'insert_after': 'against_income_account', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_coupons', 'label': 'POS Coupons Detail', 'fieldtype': 'Table', 'insert_after': 'posa_offers', 'options': 'POS Coupon Detail', 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': '', 'description': None},
		{'fieldname': 'posa_offers', 'label': 'POS Offers Detail', 'fieldtype': 'Table', 'insert_after': 'pricing_rules', 'options': 'POS Offer Detail', 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_delivery_charges_rate', 'label': 'Delivery Charges Rate', 'fieldtype': 'Currency', 'insert_after': 'posa_delivery_charges', 'options': 'currency', 'depends_on': None, 'reqd': 0, 'hidden': 1, 'default': None, 'description': None},
		{'fieldname': 'posa_delivery_charges', 'label': 'Delivery Charges', 'fieldtype': 'Link', 'insert_after': 'taxes_and_charges', 'options': 'Delivery Charges', 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_is_printed', 'label': 'Printed', 'fieldtype': 'Check', 'insert_after': 'posa_pos_opening_shift', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_pos_opening_shift', 'label': 'POS Shift', 'fieldtype': 'Data', 'insert_after': 'pos_profile', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None}
		],
		"Sales Order": [
		{'fieldname': 'posa_coupons', 'label': 'POS Coupons Detail', 'fieldtype': 'Table', 'insert_after': 'posa_offers', 'options': 'POS Coupon Detail', 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_offers', 'label': 'POS Offers Detail', 'fieldtype': 'Table', 'insert_after': 'pricing_rules', 'options': 'POS Offer Detail', 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_notes', 'label': 'Additional Notes', 'fieldtype': 'Small Text', 'insert_after': 'posa_additional_notes_section', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_additional_notes_section', 'label': 'Additional Notes', 'fieldtype': 'Section Break', 'insert_after': 'items', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None}
		],
		"Customer":[
		{'fieldname': 'posa_referral_company', 'label': 'Referral Company', 'fieldtype': 'Link', 'insert_after': 'posa_referral_code', 'options': 'Company', 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_referral_code', 'label': 'Referral Code', 'fieldtype': 'Data', 'insert_after': 'posa_referral_section', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_referral_section', 'label': 'Referral Code', 'fieldtype': 'Section Break', 'insert_after': 'posa_birthday', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_birthday', 'label': 'Birthday', 'fieldtype': 'Date', 'insert_after': 'contact_html', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_discount', 'label': 'Discount %', 'fieldtype': 'Float', 'insert_after': 'lead_name', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': '0', 'description': None}
		],
		"Address": [
		{'fieldname': 'posa_delivery_charges', 'label': 'Delivery Charges', 'fieldtype': 'Link', 'insert_after': 'is_shipping_address', 'options': 'Delivery Charges', 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': '', 'description': None}
		],
		"Company": [
		{'fieldname': 'posa_referral_campaign', 'label': 'Referral Campaign', 'fieldtype': 'Link', 'insert_after': 'posa_primary_offer', 'options': 'Campaign', 'depends_on': 'posa_auto_referral', 'reqd': 0, 'hidden': 0, 'default': '', 'description': None},
		{'fieldname': 'posa_primary_offer', 'label': 'Primary Customer Offer', 'fieldtype': 'Link', 'insert_after': 'posa_customer_offer', 'options': 'POS Offer', 'depends_on': 'posa_auto_referral', 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_customer_offer', 'label': 'Final Customer Offer', 'fieldtype': 'Link', 'insert_after': 'posa_column_break_22', 'options': 'POS Offer', 'depends_on': 'posa_auto_referral', 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_column_break_22', 'label': '', 'fieldtype': 'Column Break', 'insert_after': 'posa_auto_referral', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_auto_referral', 'label': 'Auto Create Referral For New Customers', 'fieldtype': 'Check', 'insert_after': 'posa_referral_section', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_referral_section', 'label': 'Referral Code', 'fieldtype': 'Section Break', 'insert_after': 'total_monthly_sales', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None}
		],
		"Batch": [
		{'fieldname': 'posa_batch_price', 'label': 'Price', 'fieldtype': 'Float', 'insert_after': 'manufacturing_date', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': '0', 'description': None}
		],
		"Item Barcode": [
		{'fieldname': 'posa_uom', 'label': 'UOM', 'fieldtype': 'Link', 'insert_after': 'barcode_type', 'options': 'UOM', 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None}
		],
		"Sales Invoice Item": [
		{'fieldname': 'posa_is_replace', 'label': 'Is Offer Replace For item Row ID', 'fieldtype': 'Data', 'insert_after': 'posa_is_offer', 'options': None, 'depends_on': '', 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_is_offer', 'label': 'Is Offer', 'fieldtype': 'Check', 'insert_after': 'posa_offer_applied', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_offer_applied', 'label': 'Offer Applied', 'fieldtype': 'Check', 'insert_after': 'posa_offers', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_offers', 'label': 'POS Offers', 'fieldtype': 'Small Text', 'insert_after': 'pricing_rules', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_delivery_date', 'label': 'Delivery Date', 'fieldtype': 'Date', 'insert_after': 'posa_row_id', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_row_id', 'label': 'Row ID', 'fieldtype': 'Data', 'insert_after': 'item_name', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_notes', 'label': 'Additional Notes', 'fieldtype': 'Small Text', 'insert_after': 'item_code', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None}
		],
		"Sales Order Item": [
		{'fieldname': 'posa_row_id', 'label': 'Row ID', 'fieldtype': 'Data', 'insert_after': 'item_name', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None},
		{'fieldname': 'posa_notes', 'label': 'Additional Notes', 'fieldtype': 'Small Text', 'insert_after': 'ensure_delivery_based_on_produced_serial_no', 'options': None, 'depends_on': None, 'reqd': 0, 'hidden': 0, 'default': None, 'description': None}
		],
	}
