import datetime
import json

import frappe
import pytz
from frappe import _

no_cache = 1

@frappe.whitelist(allow_guest=True)
def get_asset_info(asset_code):
    context = {}
    context["asset_info"] = None

    if asset_code:
        # applicant_info = frappe.get_all(
        #     "Asset",
        #     filters={"name": asset_code},
        #     fields=["", "applicant_name", "cid", "gender", "employment_type", "applicant_rank", "application_status", "mobile_no", "flat_no","building_classification","application_date_time","work_station"],
        # )
        asset_info = frappe.db.sql(
            """
                select case when is_hostel_asset="Hostel Room" then hostel
                        when is_hostel_asset = "Room" then (select `tabRoom`.room_name from `tabRoom` where `tabRoom`.name = `tabAsset`.roombuilding)
                        else concat(custodian, ' - ', custodian_name) end as custodian,
                        purchase_date, concat("BTN. ", format(gross_purchase_amount,2)) as asset_rate, name, asset_name from `tabAsset` where name = '{}'
            """.format(asset_code), as_dict=1
        )
        context["asset_info"] = asset_info
    
    return context
