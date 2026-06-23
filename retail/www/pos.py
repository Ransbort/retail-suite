import frappe
import os

no_cache = 1

def get_context(context):
    index_path = os.path.join(
        frappe.local.sites_path,
        "assets/retail/retail_suite/index.html"
    )
    with open(index_path) as f:
        context.index_html = f.read()
