import frappe
from frappe import _
from frappe.utils.caching import redis_cache
from frappe.utils import nowdate, flt, nowdate
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count
from frappe.utils.background_jobs import enqueue
from erpnext.stock.get_item_details import get_item_details
from retail.retail.api.pricing_rule import apply_pricing_rules_for_pos
from erpnext.stock.doctype.batch.batch import (get_batch_no, get_batch_qty)
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from erpnext.accounts.doctype.loyalty_program.loyalty_program import get_loyalty_program_details_with_points
def pos_cache(fn, pos_profile: dict):

    if not pos_profile.get("posa_use_server_cache"):
        return fn

    ttl = pos_profile.get("posa_server_cache_duration")
    ttl = int(ttl) * 30 if ttl else 1800
    return redis_cache(ttl=ttl)(fn)

def get_search_mode_settings(pos_profile : dict):
    """Returns the search mode settings for the given pos profile"""
    if pos_profile.get("posa_search_batch_no"):
            return "batch"
    if pos_profile.get("posa_search_serial_no"):
        return "serial"
    if pos_profile.get("posa_search_barcode_no"):
        return "barcode"
    return None

def build_item_search_data(item, search_mode, warehouse, today):
    """Builds the search data for the given item"""
    item_code = item["item_code"]
    item["batch_no_data"] = []
    item["serial_no_data"] = []
    item["item_barcode"] = []

    if search_mode == "batch":
        batch_list = get_batch_qty(warehouse=warehouse, item_code=item_code)
        if batch_list:
            for batch in batch_list:
                if batch.qty > 0 and batch.batch_no:
                    batch_doc = frappe.get_cached_doc(
                        "Batch", batch.batch_no
                    )
                    if (
                        str(batch_doc.expiry_date) > str(today)
                        or batch_doc.expiry_date in ["", None]
                    ) and batch_doc.disabled == 0:
                        item["batch_no_data"].append(
                            {
                                "batch_no": batch.batch_no,
                                "batch_qty": batch.qty,
                                "expiry_date": batch_doc.expiry_date,
                                "batch_price": batch_doc.posa_batch_price,
                                "manufacturing_date": batch_doc.manufacturing_date,
                            }
                        )

    elif search_mode == "serial":
        item["serial_no_data"] = frappe.get_all(
            "Serial No",
            filters={"item_code": item_code, "status": "Active", "warehouse": warehouse},
            fields=["name as serial_no"],
        )

    elif search_mode == "barcode":
        item["item_barcode"] = frappe.get_all(
            "Item Barcode",
            filters={"parent": item_code},
            fields=["barcode", "posa_uom", "uom", "barcode_type", "parent as item_code"],
        )
    return item

def get_item_attributes(item_code):
    attributes = frappe.db.get_all(
        "Item Variant Attribute",
        fields=["attribute"],
        filters={"parenttype": "Item", "parent": item_code},
        order_by="name asc",
    )

    optional_attributes = get_item_optional_attributes(item_code)

    for a in attributes:
        values = frappe.db.get_all(
            "Item Attribute Value",
            fields=["attribute_value", "abbr"],
            filters={"parenttype": "Item Attribute", "parent": a.attribute},
            order_by="abbr asc",
        )
        a.values = values
        if a.attribute in optional_attributes:
            a.optional = True

    return attributes

def attach_stock_and_attributes(item: dict, warehouse: str, posa_show_template_items: bool) -> dict:
    """Attaches stock qty and variant attributes to the item."""
    item_code = item["item_code"]

    item["actual_qty"] = get_stock_availability(item_code, warehouse) or 0 if warehouse else 0

    item["attributes"] = ""
    if posa_show_template_items and item.get("has_variants"):
        item["attributes"] = get_item_attributes(item_code)

    item["item_attributes"] = ""
    if posa_show_template_items and item.get("variant_of"):
        item["item_attributes"] = frappe.get_all(
            "Item Variant Attribute",
            fields=["attribute", "attribute_value"],
            filters={"parent": item_code, "parentfield": "attributes"},
        )

    return item

def _get_uom_conversions(item_code: str) -> dict:
    """Returns {uom: conversion_factor} for an item."""
    conversions = frappe.get_all(
        "UOM Conversion Detail",
        filters={"parent": item_code},
        fields=["uom", "conversion_factor"],
    )
    return {d.uom: d.conversion_factor for d in conversions}

def _build_prices(items_data, price_list, customer, pos_profile, today):
    items = [d["item_code"] for d in items_data]
    prices =  frappe.get_all(
            "Item Price",
            fields=["item_code", "price_list_rate", "currency", "uom"],
            filters={
                "price_list": price_list,
                "item_code": ["in", items],
                "currency": pos_profile.get("currency"),
                "selling": 1,
                "valid_from": ["<=", today],
                "customer": ["in", ["", None, customer]],
            },
            order_by="valid_from ASC, valid_upto DESC",
        )

    price_map = {}

    for p in prices:
        price_map.setdefault(p.item_code, {})
        price_map[p.item_code][p.uom or "None"] = p

    return price_map

def _build_pricing_rule(items_data, price_map, customer, pos_profile, price_list, today):
    customer_group = frappe.db.get_value("Customer", customer, "customer_group") if customer else None

    pos_items = []

    for item in items_data:
        item_code = item["item_code"]
        item_price = price_map.get(item_code, {})

        pos_items.append({
            "doctype": "Sales Invoice Item",
            "name": item_code,
            "item_code": item_code,
            "item_group": item.get("item_group"),
            "brand": item.get("brand"),
            "qty": 1,
            "uom": item.get("stock_uom"),
            "conversion_factor": 1,
            "price_list_rate": item_price.get("price_list_rate", 0),
            "parenttype": "Sales Invoice",
        })

    pricing_rule_details = apply_pricing_rules_for_pos(
        items=pos_items,
        customer=customer,
        customer_group=customer_group,
        company=pos_profile.get("company"),
        price_list=price_list,
        currency=pos_profile.get("currency"),
        transaction_date=today,
    ) or []

    rule_map = {}

    for rule in pricing_rule_details:
        key = rule.get("item_code") or rule.get("name")
        if key:
            rule_map[key] = rule

    return rule_map

def _get_item_price(price_map, item_code, stock_uom):
    """Returns the best matching price record."""
    uom_prices = price_map.get(item_code, {})
    return (
        uom_prices.get(stock_uom)   # ← stock_uom أول
        or uom_prices.get("None")   # ← fallback
        or {}
    )

def _get_uom_conversions(item_code: str) -> dict:
    """Returns {uom: conversion_factor} for an item."""
    conversions = frappe.get_all(
        "UOM Conversion Detail",
        filters={"parent": item_code},
        fields=["uom", "conversion_factor"],
    )
    return {d.uom: d.conversion_factor for d in conversions}

def _calculate_item_price(item, price_map, rule_map, allow_zero_rated_items, pos_profile):
    item_code = item.item_code
    item_price = _get_item_price(price_map, item_code, item.stock_uom)
    rule = rule_map.get(item_code, {})

    original_rate = item_price.get("price_list_rate") or 0
    discount_percentage = rule.get("discount_percentage", 0)
    discount_amount = rule.get("discount_amount", 0)
    final_rate = original_rate

    if discount_percentage:
        final_rate = flt(original_rate * (1 - flt(discount_percentage) / 100), 2)
    elif discount_amount:
        final_rate = flt(original_rate - discount_amount, 2)

    if not allow_zero_rated_items and flt(final_rate) <= 0:
        return None

    currency = item_price.get("currency") or pos_profile.get("currency")
    uom_conversions = _get_uom_conversions(item_code)
    stock_uom_price = item_price.get("price_list_rate") or 0

    uom_prices = {}
    for uom, cf in uom_conversions.items():
        # لو موجود في price_map استخدمه — لو لأ احسبه من stock_uom
        if uom in price_map.get(item_code, {}):
            uom_original = price_map[item_code][uom].get("price_list_rate") or 0
        else:
            uom_original = flt(stock_uom_price * cf, 2)

        uom_final = uom_original
        if discount_percentage:
            uom_final = flt(uom_original * (1 - flt(discount_percentage) / 100), 2)
        elif discount_amount:
            uom_final = flt(uom_original - (discount_amount * cf), 2)

        uom_prices[uom] = {
            "original_rate": uom_original,
            "rate": uom_final,
            "discount_percentage": discount_percentage,
            "discount_amount": discount_amount,
            "pricing_rules": rule.get("pricing_rules"),
            "currency": currency,
            "conversion_factor": cf,
        }

    return {
        "uom_prices": uom_prices,
    }

@frappe.whitelist()
def get_items(pos_profile, price_list=None, item_group="", search_value="", customer=None, warehouse=None):
    _pos_profile = frappe.parse_json(pos_profile)
    price_list = price_list or _pos_profile.get("selling_price_list")

    if search_value or item_group or warehouse or customer:
        return _get_items(
            pos_profile, price_list, item_group, search_value, customer, warehouse
        )

    return pos_cache(_get_items, _pos_profile)(
        pos_profile, price_list, item_group, search_value, customer, warehouse
    )

def resolve_pos_search(search_value: str) -> dict:
    """Auto-detect search type and return resolved data."""
    if not search_value:
        return {}

    # Serial No
    serial = frappe.db.get_value(
        "Serial No", search_value,
        ["name as serial_no", "item_code"],
        as_dict=True
    )
    if serial:
        return {
            "type": "serial",
            "item_code": serial.item_code,
            "serial_no": serial.serial_no,
        }

    # Batch
    batch = frappe.db.get_value(
        "Batch", search_value,
        ["name as batch_no", "item as item_code"],
        as_dict=True
    )
    if batch:
        return {
            "type": "batch",
            "item_code": batch.item_code,
            "batch_no": batch.batch_no,
        }

    # Barcode
    barcode = frappe.db.get_value(
        "Item Barcode",
        {"barcode": search_value},
        ["parent as item_code", "uom", "barcode_type"],
        as_dict=True
    )
    if barcode:
        return {
            "type": "barcode",
            "item_code": barcode.item_code,
            "uom": barcode.uom,
            "barcode": search_value,
        }

    # Text search
    return {
        "type": "text",
        "item_code": search_value,
    }

def _get_items(pos_profile, price_list, item_group, search_value, customer=None, warehouse=None):
    pos_profile = frappe.parse_json(pos_profile)
    today = nowdate()
    posa_display_items_in_stock = pos_profile.get("posa_display_items_in_stock")
    posa_show_template_items = pos_profile.get("posa_show_template_items")
    warehouse = warehouse or pos_profile.get("warehouse")
    search_limit = pos_profile.get("posa_search_limit") or 100
    use_limit_search = pos_profile.get("posa_use_limit_search")
    allow_zero_rated_items = pos_profile.get("posa_allow_zero_rated_items")
    search_mode = get_search_mode_settings(pos_profile)
    price_list = price_list or pos_profile.get("selling_price_list")
    data = dict()
    search_context = {}

    Item = DocType("Item")
    query = (
        frappe.qb.from_(Item)
        .select(
            Item.name.as_("item_code"),
            Item.item_name,
            Item.description,
            Item.stock_uom,
            Item.image,
            Item.is_stock_item,
            Item.has_variants,
            Item.variant_of,
            Item.item_group,
            Item.has_batch_no,
            Item.has_serial_no,
            Item.max_discount,
            Item.brand,
            Item.disabled,
        )
        .where(
            (Item.disabled == 0)
            & (Item.is_sales_item == 1)
            & (Item.is_fixed_asset == 0)
        )
        .orderby(Item.item_name)
    )

    item_groups = get_item_group_condition(pos_profile.get("name"))

    if item_groups:
        query = query.where(Item.item_group.isin(item_groups))

    if not posa_show_template_items:
        query = query.where(Item.has_variants == 0)

    if use_limit_search:
        if search_value:
            data = resolve_pos_search(search_value)
            search_context = {
                "type": data.get("type"),
                "item_code": data.get("item_code"),
                "barcode": data.get("barcode"),
                "uom": data.get("uom"),
                "serial_no": data.get("serial_no"),
                "batch_no": data.get("batch_no"),
            }

        item_code = data.get("item_code") or search_value
        serial_no = data.get("serial_no") or ""
        batch_no = data.get("batch_no") or ""
        barcode = data.get("barcode") or ""

        if serial_no or batch_no or barcode:
            query = query.where(Item.name == item_code)
        elif item_code:
            query = query.where(
                (Item.name.like(f"%{item_code}%")) | (Item.item_name.like(f"%{item_code}%"))
            )

        if item_group:
            query = query.where(Item.item_group.like(f"%{item_group}%"))

        query = query.limit(int(search_limit))

    items_data = query.run(as_dict=True)
    print("Items Data:", items_data)

    result = []
    if items_data:
        price_map = _build_prices(items_data, price_list, customer, pos_profile, today)
        rule_map = _build_pricing_rule(items_data, price_map, customer, pos_profile, price_list, today)
        for item in items_data:
            pricing = _calculate_item_price(item, price_map, rule_map, allow_zero_rated_items, pos_profile)
            if pricing is None:
                continue
            item = build_item_search_data(item, search_mode, warehouse, today)
            item = attach_stock_and_attributes(item, warehouse, posa_show_template_items)
            if posa_display_items_in_stock and item["actual_qty"] <= 0:
                continue
            item.update({
                **pricing,
                "warehouse": pos_profile.get("warehouse"),
                "use_limit_search": use_limit_search,
            })
            result.append(item)

    return {
        "items": result,
        "search_context": search_context if use_limit_search else {}
    }

def get_item_group_condition(pos_profile):
    item_groups = get_item_groups(pos_profile)
    if item_groups:
        return [i.strip("'") for i in item_groups]
    return []

def get_customer_groups(pos_profile):
    customer_groups = []
    if pos_profile.get("customer_groups"):
        # Get items based on the item groups defined in the POS profile
        for data in pos_profile.get("customer_groups"):
            customer_groups.extend(
                [
                    "%s" % frappe.db.escape(d.get("name"))
                    for d in get_child_nodes(
                        "Customer Group", data.get("customer_group")
                    )
                ]
            )

    return list(set(customer_groups))

def get_child_nodes(group_type, root):
    if not frappe.get_meta(group_type):
        frappe.throw("Invalid DocType")
    lft, rgt = frappe.db.get_value(group_type, root, ["lft", "rgt"])
    return frappe.db.get_all(
        group_type,
        filters=[["lft", ">=", lft], ["rgt", "<=", rgt]],
        fields=["name", "lft", "rgt"],
        order_by="lft asc",
    )

def get_stock_availability(item_code, warehouse):
    actual_qty = (
        frappe.db.get_value(
            "Stock Ledger Entry",
            filters={
                "item_code": item_code,
                "warehouse": warehouse,
                "is_cancelled": 0,
            },
            fieldname="qty_after_transaction",
            order_by="posting_date desc, posting_time desc, creation desc",
        )
        or 0.0
    )
    return actual_qty

def build_item_cache(item_code):
    parent_item_code = item_code

    attributes = [
        a.attribute
        for a in frappe.db.get_all(
            "Item Variant Attribute",
            {"parent": parent_item_code},
            ["attribute"],
            order_by="name asc",
        )
    ]

    item_variants_data = frappe.db.get_all(
        "Item Variant Attribute",
        {"variant_of": parent_item_code},
        ["parent", "attribute", "attribute_value"],
        order_by="name",
        as_list=1,
    )

    disabled_items = set([i.name for i in frappe.db.get_all("Item", {"disabled": 1})])

    attribute_value_item_map = frappe._dict({})
    item_attribute_value_map = frappe._dict({})

    item_variants_data = [r for r in item_variants_data if r[0] not in disabled_items]
    for row in item_variants_data:
        item_code, attribute, attribute_value = row
        # (attr, value) => [item1, item2]
        attribute_value_item_map.setdefault((attribute, attribute_value), []).append(
            item_code
        )
        # item => {attr1: value1, attr2: value2}
        item_attribute_value_map.setdefault(item_code, {})[attribute] = attribute_value

    optional_attributes = set()
    for item_code, attr_dict in item_attribute_value_map.items():
        for attribute in attributes:
            if attribute not in attr_dict:
                optional_attributes.add(attribute)

    frappe.cache().hset(
        "attribute_value_item_map", parent_item_code, attribute_value_item_map
    )
    frappe.cache().hset(
        "item_attribute_value_map", parent_item_code, item_attribute_value_map
    )
    frappe.cache().hset("item_variants_data", parent_item_code, item_variants_data)
    frappe.cache().hset("optional_attributes", parent_item_code, optional_attributes)

def get_item_optional_attributes(item_code):
    val = frappe.cache().hget("optional_attributes", item_code)

    if not val:
        build_item_cache(item_code)

    return frappe.cache().hget("optional_attributes", item_code)

def get_search_items_conditions(item_code, serial_no, batch_no, barcode):
    if serial_no or batch_no or barcode:
        return " and name = {0}".format(frappe.db.escape(item_code))
    return """ and (name like {item_code} or item_name like {item_code})""".format(
        item_code=frappe.db.escape("%" + item_code + "%")
    )

def get_customer_group_condition(pos_profile):
    customer_groups = get_customer_groups(pos_profile)
    if customer_groups:
        placeholders = ", ".join(["%s"] * len(customer_groups))
        return f"customer_group IN ({placeholders})", list(customer_groups)  # nosemgrep
    return "1=1", []

@frappe.whitelist()
def get_customer_names(pos_profile):
    return _get_customer_names(pos_profile)

def _get_customer_names(pos_profile):
    pos_profile = frappe.parse_json(pos_profile)
    filters = {"disabled": 0}

    customer_groups = get_customer_groups(pos_profile)
    if customer_groups:
        filters["customer_group"] = ["in", customer_groups]
    else:
        filters["name"] = pos_profile.get("customer")

    return frappe.db.get_all(
        "Customer",
        filters=filters,
        fields=["name", "customer_name", "territory", "customer_type"],
        order_by="name asc"
    )

def _has_address_data(payload: dict) -> bool:
    """Only treat address as provided if a meaningful field was actually filled in.
    Skips 'country' (always has a default) and the is_primary/is_shipping flags."""
    meaningful_fields = ("line1", "line2", "city", "state", "pincode")
    return any(payload.get(f) for f in meaningful_fields)

@frappe.whitelist()
def create_customer(
    customer_name,
    company,
    pos_profile_doc,
    first_mobile,
    city,
    customer_id=None,
    second_mobile=None,
    email_id=None,
    customer_group=None,
    territory=None,
    customer_type=None,
    gender=None,
    method="create",
    note='',
    # contact fields
    first_name=None,
    last_name=None,
    # address fields
    address_line1=None,
    address_line2=None,
    state=None,
    country="Egypt",
    pincode=None):
    from retail.retail.api.contact import create_contact, update_contact
    from retail.retail.api.address import create_address, update_address, get_customer_addresses

    pos_profile = frappe.parse_json(pos_profile_doc) if isinstance(pos_profile_doc, str) else pos_profile_doc

    # ── بيانات الكونتكت ──────────────────────────────────────────────
    phone_nos = [
        {"phone": first_mobile, "is_primary_mobile_no": 1, "is_primary_phone": 1},
    ]
    if second_mobile:
        phone_nos.append({"phone": second_mobile, "is_primary_mobile_no": 0, "is_primary_phone": 0})

    email_ids = [{"email_id": email_id, "is_primary": 1}] if email_id else []

    # ── بيانات الأدريس ──────────────────────────────────────────────
    address_payload = {
        "title"              : customer_name,
        "line1"              : address_line1 or city,
        "line2"              : address_line2 or "",
        "city"               : city,
        "state"              : state  or "",
        "country"            : country or "Egypt",
        "pincode"            : pincode or "",
        "is_primary_address" : 1,
        "is_shipping_address": 1,
    }

    # ════════════════════════════════════════════════════════════════
    if method == "create":
        is_exist = frappe.db.exists("Customer", {"customer_name": customer_name})
        if not pos_profile.get("posa_allow_duplicate_customer_names") and is_exist:
            frappe.throw(_("Customer already exists"))

        # 1. Customer
        customer_doc = frappe.get_doc({
            "doctype"             : "Customer",
            "customer_name"       : customer_name,
            "posa_referral_company": company,
            "customer_type"       : customer_type or "",
            "gender"              : gender or "",
            "custom_note"         : note or "",
            "customer_group"      : customer_group or "",
            "territory"           : territory      or "",
        })
        customer_doc.insert(ignore_permissions=False)


        cust_name = customer_doc.name

        # 2. Address — only create if the user actually entered address data
        saved_address = None
        if _has_address_data(address_payload):
            saved_address = create_address(
                customer=cust_name,
                **address_payload
            )

        # 3. Contact
        create_contact(
            customer     = cust_name,
            first_name   = first_name or customer_name,
            last_name    = last_name  or "",
            is_primary   = 1,
            email_ids    = email_ids,
            phone_nos    = phone_nos,
            address_name = saved_address["name"] if saved_address else None,
        )

        return customer_doc

    # ════════════════════════════════════════════════════════════════
    elif method == "update":
        customer_doc = frappe.get_doc("Customer", customer_id)
        customer_doc.customer_name = customer_name
        if company:       customer_doc.posa_referral_company = company
        if customer_type: customer_doc.customer_type         = customer_type
        if gender:        customer_doc.gender                = gender
        if note:          customer_doc.custom_note           = note
        if customer_group: customer_doc.customer_group       = customer_group
        if territory:      customer_doc.territory            = territory

        customer_doc.save(ignore_permissions=False)

        # ── Contact ──────────────────────────────────────────────
        from frappe.contacts.doctype.contact.contact import get_contacts_linking_to
        contacts = get_contacts_linking_to("Customer", customer_id, fields=["name", "address"])
        primary_contact = next(
            (c for c in contacts if frappe.db.get_value("Contact", c["name"], "is_primary_contact")),
            contacts[0] if contacts else None
        )

        contact_payload = {
            "first_name" : first_name or customer_name,
            "last_name"  : last_name  or "",
            "is_primary" : 1,
            "email_ids"  : email_ids,
            "phone_nos"  : phone_nos,
        }

        # ── Address ──────────────────────────────────────────────
        existing_addresses = get_customer_addresses(customer_id)
        primary_address = next(
            (a for a in existing_addresses if a.get("is_primary_address")),
            existing_addresses[0] if existing_addresses else None
        )

        if primary_address:
            saved_address = update_address(primary_address["name"], **address_payload)
            contact_payload["address_name"] = primary_address["name"]
        else:
            # only create if the user actually entered address data
            saved_address = None
            if _has_address_data(address_payload):
                saved_address = create_address(customer=customer_id, **address_payload)
            contact_payload["address_name"] = saved_address["name"] if saved_address else None

        if primary_contact:
            update_contact(primary_contact["name"], **contact_payload)
        else:
            create_contact(customer=customer_id, **contact_payload)

        return customer_doc

@frappe.whitelist()
def get_customer_info(customer):
    customer = frappe.get_doc("Customer", customer)

    res = {"loyalty_points": None, "conversion_factor": None}

    res["email_id"] = customer.email_id
    res["territory"] = customer.territory
    res["customer_group"] = customer.customer_group
    res["image"] = customer.image
    res["loyalty_program"] = customer.loyalty_program
    res["customer_price_list"] = customer.default_price_list
    res["customer_group"] = customer.customer_group
    res["customer_type"] = customer.customer_type
    res["territory"] = customer.territory
    res["birthday"] = customer.posa_birthday
    res["gender"] = customer.gender
    res["tax_id"] = customer.tax_id
    res["posa_discount"] = customer.posa_discount
    res["name"] = customer.name
    res["customer_name"] = customer.customer_name
    res["customer_group_price_list"] = frappe.get_value(
        "Customer Group", customer.customer_group, "default_price_list"
    )

    if customer.loyalty_program:
        lp_details = get_loyalty_program_details_with_points(
            customer.name,
            customer.loyalty_program,
            silent=True,
            include_expired_entry=False,
        )
        res["loyalty_points"] = lp_details.get("loyalty_points")
        res["conversion_factor"] = lp_details.get("conversion_factor")

    from retail.retail.api.contact import get_party_contact_info
    res["contacts"] = get_party_contact_info("Customer", customer.name)
    from retail.retail.api.address import get_customer_addresses
    res["addresses"] = get_customer_addresses(customer.name)
    return res
