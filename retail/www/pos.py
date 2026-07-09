import frappe

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/login?redirect-to=/pos"
        raise frappe.Redirect

    html = frappe.read_file("assets/retail/retail_suite/index.html")

    csrf_token = frappe.sessions.get_csrf_token()
    boot_script = (
        f'<script>window.csrf_token = "{csrf_token}";</script>'
    )
    html = html.replace("</head>", boot_script + "</head>", 1)

    context.index_html = html
