# Copyright (c) 2026, Ahmed Abu-khatwa and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt
from retail.retail.api.shifts import get_shift_pos_transactions
from retail.retail.api.invoice import get_draft_invoices
from retail.retail.api.payment_utils import get_shift_invoice_payments, get_shift_unallocated_payments, get_shift_pos_invoices, get_shift_payments_entries, submit_printed_invoices
from frappe.utils import format_time, datetime, get_datetime

class POSClosingShift(Document):
    def validate(self):
        user = frappe.get_all(
            "POS Closing Shift",
            filters={
                "user": self.user,
                "docstatus": 1,
                "pos_opening_shift": self.pos_opening_shift,
                "name": ["!=", self.name],
            },
        )

        if user:
            frappe.throw(
                _(
                    "POS Closing Shift {} against {} between selected period".format(
                        frappe.bold("already exists"), frappe.bold(self.user)
                    )
                ),
                title=_("Invalid Period"),
            )

        if (
            frappe.db.get_value("POS Opening Shift", self.pos_opening_shift, "status")
            != "Open"
        ):
            frappe.throw(
                _("Selected POS Opening Shift should be open."),
                title=_("Invalid Opening Entry"),
            )
        if (
            frappe.db.get_value("POS Opening Shift", self.pos_opening_shift, "status")
            == "Open"
        ):
            if not frappe.get_value("POS Profile", self.pos_profile, "custom_allow_close_shift_with_draft_invoice"):
                if get_draft_invoices(self.pos_opening_shift):
                    frappe.throw(
                    _("You should Close your Draft invoice."),
                    title=_("Invoice Draft"),
                )
        self.update_payment_reconciliation()

    def update_payment_reconciliation(self):
        precision = (
            frappe.get_cached_value("System Settings", None, "currency_precision") or 3
        )
        # differnce  = closing_amount - (opening_amount + expected_amount)
        for d in self.payment_reconciliation:
            d.difference = +flt(d.closing_amount, precision) - (flt(d.opening_amount, precision) + flt(d.expected_amount, precision))

    def on_submit(self):
        opening_entry = frappe.get_doc("POS Opening Shift", self.pos_opening_shift)
        opening_entry.pos_closing_shift = self.name
        opening_entry.set_status()
        self.delete_draft_invoices()
        submit_printed_invoices(opening_entry.name)
        opening_entry.save()

    def delete_draft_invoices(self):
        if frappe.get_value("POS Profile", self.pos_profile, "posa_allow_delete"):
            data = frappe.db.sql(
                """
                select
                    name
                from
                    `tabSales Invoice`
                where
                    docstatus = 0 and posa_is_printed = 0 and posa_pos_opening_shift = %s
                """,
                (self.pos_opening_shift),
                as_dict=1,
            )

            for invoice in data:
                frappe.delete_doc("Sales Invoice", invoice.name, force=1)

    @frappe.whitelist()
    def get_payment_reconciliation_details(self):
        currency = frappe.get_cached_value("Company", self.company, "default_currency")
        template = frappe.get_template(
            "templates/pos_closing_shift/pos_closing_shift.html"
        )
        return template.render({"data": self, "currency": currency})

@frappe.whitelist()
def get_cashiers(doctype, txt, searchfield, start, page_len, filters):
    cashiers_list = frappe.get_all("POS Profile User", filters=filters, fields=["user"])
    return [c["user"] for c in cashiers_list]


@frappe.whitelist()
def get_pos_invoices(pos_opening_shift):
    return get_shift_pos_invoices(pos_opening_shift)

@frappe.whitelist()
def get_all_pos_invoices(**kwargs):

    docstatus = int(kwargs.get("docstatus", 1))
    filters = {"is_pos": 1, "docstatus": docstatus}
    if kwargs.get("pos_opening_shift"):
        filters["posa_pos_opening_shift"] = kwargs["pos_opening_shift"]

    invoices = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=["name", "owner","customer", "grand_total", "posting_date", "posting_time", "status", "posa_pos_opening_shift"],
        order_by="posting_date desc"
    )

    for inv in invoices:
        items = frappe.get_all(
            "Sales Invoice Item",
            filters={"parent": inv["name"]},
            fields=["*"]
        )
        inv["items_count"] = len(items)
        inv["items"] = items
        inv["total_qty"] = sum(i["qty"] for i in items)

    total = sum(i.get("grand_total", 0) for i in invoices)
    count = len(invoices)
    return {
        "count": count,
        "total": total,
        "invoices": invoices
    }

@frappe.whitelist()
def get_payments_entries(pos_opening_shift):
    return get_shift_payments_entries(pos_opening_shift)

@frappe.whitelist()
def make_closing_shift_from_opening(opening_shift :dict, closing_details :list):
    opening_shift = frappe.parse_json(opening_shift)
    closing_details = frappe.parse_json(closing_details)

    closing_shift = frappe.new_doc("POS Closing Shift")
    closing_shift.pos_opening_shift = opening_shift.get("name")
    closing_shift.period_start_date = opening_shift.get("period_start_date")
    closing_shift.period_end_date = frappe.utils.get_datetime()
    closing_shift.pos_profile = opening_shift.get("pos_profile")
    closing_shift.user = opening_shift.get("user")
    closing_shift.company = opening_shift.get("company")
    closing_shift.grand_total = 0
    closing_shift.net_total = 0
    closing_shift.total_quantity = 0

    invoices = get_pos_invoices(opening_shift.get("name"))

    pos_invoices = []
    taxes = []
    pos_payments_table = []

    payments = {}
    for row in opening_shift.get("balance_details", []):
        mop = row.get("mode_of_payment")
        amt = flt(row.get("amount") or 0)

        payments[mop] = frappe._dict({
            "mode_of_payment": mop,
            "opening_amount":amt,
            "expected_amount": 0,
            "closing_amount": 0,
        })


    for inv in invoices:
        pos_invoices.append(frappe._dict({
            "sales_invoice": inv.name,
            "posting_date": inv.posting_date,
            "grand_total": inv.grand_total,
            "customer": inv.customer,
        }))
        closing_shift.grand_total += flt(inv.grand_total)
        closing_shift.net_total += flt(inv.net_total)
        closing_shift.total_quantity += flt(inv.total_qty)

        for t in inv.taxes:
            existing_tax = next((tx for tx in taxes if tx.account_head == t.account_head and tx.rate == t.rate), None)
            if existing_tax:
                existing_tax.amount += flt(t.tax_amount)
            else:
                taxes.append(frappe._dict({
                    "account_head": t.account_head,
                    "rate": t.rate,
                    "amount": t.tax_amount,
                }))

        if inv.payments:
            for p in inv.payments:
                mop = p.mode_of_payment
                payments[mop].expected_amount += flt(p.amount)

        payment_entries = get_shift_invoice_payments(inv["name"])
        for pe in payment_entries:
            mop = pe["mode_of_payment"]
            payments[mop]["expected_amount"] += pe["allocated_to_this_invoice"]


    pos_payments = get_payments_entries(opening_shift.get("name"))

    for py in pos_payments:
        pos_payments_table.append(
            frappe._dict(
                {
                    "payment_entry": py.name,
                    "mode_of_payment": py.mode_of_payment,
                    "paid_amount": py.paid_amount,
                    "posting_date": py.posting_date,
                    "customer": py.party,
                }
            )
        )

    unallocated = get_shift_unallocated_payments(opening_shift.get("name"))
    for pe in unallocated:
        mop = pe.get("mode_of_payment")
        payments[mop]["expected_amount"] += flt(pe.get("unallocated_amount", 0))

    can_close = True
    for mop, pay in payments.items():
        closing_detail = next(
            (d for d in closing_details if d.get("modeOfPayment") == mop), None
        )
        pay.closing_amount = flt(closing_detail.get("closingBalance")) if closing_detail else 0
        diff = flt(pay.expected_amount + pay.opening_amount - pay.closing_amount, 2)
        pay.difference = diff
        if diff != 0:
            can_close = False
            frappe.throw(_("Payment difference detected for mode {0}: {1}").format(mop, diff))

    payments_list = list(payments.values())

    closing_shift.set("pos_transactions", pos_invoices)
    closing_shift.set("payment_reconciliation", payments_list)
    closing_shift.set("taxes", taxes)
    closing_shift.set("pos_payments", pos_payments_table)

    if can_close:
        if opening_shift.get("user") == frappe.session.user:
            closing_shift.insert(ignore_permissions=True)
            closing_shift.submit()

        else:
            closing_shift.insert()
            closing_shift.submit()

    return closing_shift

@frappe.whitelist()
def get_shift_summary(pos_opening_shift_name: str):

    pos_opening_shift = frappe.get_doc("POS Opening Shift", pos_opening_shift_name).as_dict()

    invoices = get_pos_invoices(pos_opening_shift.get("name"))
    pos_payments = get_payments_entries(pos_opening_shift.get("name"))

    taxes = []
    payments = []
    pos_transactions = []
    pos_payments_table = []

    for detail in (pos_opening_shift.get("balance_details") or []):
        payments.append(
            frappe._dict({
                "mode_of_payment": detail.get("mode_of_payment"),
                "opening_amount": detail.get("amount") or 0,
                "expected_amount": detail.get("amount") or 0,
                "closing_amount": 0,
            })
        )

    total_sales = 0
    total_qty = 0
    net_total = 0

    for d in invoices:
        total_sales += flt(d.grand_total)
        total_qty += flt(d.total_qty)
        net_total += flt(d.net_total)

        invoice_doc = frappe.get_doc("Sales Invoice", d.name)
        invoice_qty = sum(flt(it.qty) for it in (invoice_doc.items or []))

        is_return = flt(d.grand_total) < 0

        pos_transactions.append(frappe._dict({
            "sales_invoice": d.name,
            "posting_time": format_time(d.posting_time, "hh:mm a"),
            "posting_date": d.posting_date,
            "grand_total": d.grand_total,
            "customer": d.customer,
            "total_qty": invoice_qty,
            "Cashier": d.owner,
            "status": d.status,
            "is_return": is_return
        }))


        for t in d.taxes:
            existing_tax = [tx for tx in taxes if tx.account_head == t.account_head and tx.rate == t.rate]
            if existing_tax:
                existing_tax[0].amount += flt(t.tax_amount)
            else:
                taxes.append(frappe._dict({
                    "account_head": t.account_head,
                    "rate": t.rate,
                    "amount": t.tax_amount,
                }))

        # 🔸 المدفوعات (Sales Invoice Payments)
        for p in d.payments:
            existing_pay = [pay for pay in payments if pay.mode_of_payment == p.mode_of_payment]

            payment_amount = flt(p.amount)
            if flt(d.grand_total) < 0 and payment_amount > 0:
                payment_amount = -payment_amount

            if existing_pay:
                existing_pay[0].expected_amount += payment_amount
            else:
                payments.append(frappe._dict({
                    "mode_of_payment": p.mode_of_payment,
                    "opening_amount": 0,
                    "expected_amount": payment_amount,
                }))

    for py in pos_payments:
        pos_payments_table.append(frappe._dict({
            "payment_entry": py.name,
            "mode_of_payment": py.mode_of_payment,
            "paid_amount": py.paid_amount,
            "posting_date": py.posting_date,
            "customer": py.party,
        }))

        existing_pay = [pay for pay in payments if pay.mode_of_payment == py.mode_of_payment]
        if existing_pay:
            existing_pay[0].expected_amount += flt(py.paid_amount)
        else:
            payments.append(frappe._dict({
                "mode_of_payment": py.mode_of_payment,
                "opening_amount": 0,
                "expected_amount": py.paid_amount,
            }))

    return {
        "total_sales": total_sales,
        "net_total": net_total,
        "total_quantity": total_qty,
        "transactions": pos_transactions,
        "taxes": taxes,
        "payments": payments,
        "pos_payments": pos_payments_table
    }
