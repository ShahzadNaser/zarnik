import frappe
from frappe.utils import cint, flt

def on_submit(doc, method):
    add_manufacture_request(doc)

def on_cancel(doc, method):
    cancel_se(doc)

def add_manufacture_request(doc):
    _invoice = doc.name
    for item in doc.items:
        bom = frappe.db.get_value("BOM", {"item": item.item_code, "is_active": 1, "is_default": 1})
        manufacturing_entry_threshold = frappe.db.get_value("Item",item.item_code,"manufacturing_entry_threshold")
        #frappe.errprint(bom)
        #frappe.errprint(manufacturing_entry_threshold)

        if bom and manufacturing_entry_threshold and flt(manufacturing_entry_threshold) > flt(item.get("actual_qty") - item.get("qty")):
            doc = frappe.new_doc("Stock Entry")
            doc.stock_entry_type = "Manufacture"
            doc.purpose = "Manufacture"
            doc.from_bom = 1
            doc.use_multi_level_bom = 1
            doc.bom_no = bom
            doc.fg_completed_qty = item.get("qty") or 1
            doc.from_warehouse = item.get("warehouse")
            doc.to_warehouse = item.get("warehouse")
            doc.get_items()
            doc.remarks = _invoice
            doc.flags.ignore_permissions = True
            doc.save()
            doc.submit()

def cancel_se(doc):
    doc_list = frappe.db.get_list("Stock Entry",filters={"docstatus":1,"remarks" : doc.name})
    if doc_list:
        for se in doc_list:
            se_doc = frappe.get_doc('Stock Entry', se.name)
            se_doc.cancel()
