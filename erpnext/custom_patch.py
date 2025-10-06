import frappe
from frappe.utils import nowdate, getdate, add_days, add_months, add_years, flt, cint
from frappe import _

def update_abbreviation():
    for a in frappe.db.sql("""
        select name from `tabAccount` where name like '% - RUoB%'
    """,as_dict=1):
        new_name = a.name.replace(" - RUoB", " - RUB")
        frappe.rename_doc("Account", a.name, new_name, force=True)
        print(new_name)

def sync_child_account():
    count = 1
    # for acc in frappe.db.sql(""" SELECT b.name AS rub_account FROM `tabAccount` b WHERE b.company = 'Royal University of Bhutan'   AND NOT EXISTS (     SELECT 1     FROM `tabAccount` a     WHERE TRIM(a.name) = TRIM(REPLACE(b.name, 'RUB', 'CST'))
    #          AND a.company = 'College of Science and Technology'); """, as_dict=1):
    #          doc = frappe.get_doc("Account", acc.rub_account)
    #          doc.validate_account_currency()
    #          doc.validate_root_company_and_sync_account_to_children()
    #          print(str(count)+". "+acc.rub_account)
    #          count += 1

    for acc in frappe.db.sql(""" SELECT name AS rub_account FROM `tabAccount`  WHERE company = 'Royal University of Bhutan'
             """, as_dict=1):
             doc = frappe.get_doc("Account", acc.rub_account)
             doc.validate_account_currency()
             doc.validate_root_company_and_sync_account_to_children()
             print(str(count)+". "+acc.rub_account)
             count += 1