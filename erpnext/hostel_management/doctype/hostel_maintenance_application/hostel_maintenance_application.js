// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Maintenance Application", {
	
	refresh(frm) {
		if (!frm.doc.hostel_maintenance_report && frm.doc.docstatus == 1 && frm.doc.workflow_state == "Approved")  {
			frm.add_custom_button(__("Hostel Maintenance Report"), function () {
				frm.trigger("create_maintenance_application");
				},
				__("Create")
			);
		}
		frm.set_query("college", function(){
			return {
				filters: {
					"is_group": 0,
				}
			}
		}); 
		frm.set_query("applied_by", function() {
            return {
                filters: {
                    company: frm.doc.college
                }
            };
        });
		frm.set_query("branch", function() {
            return {
                filters: {
                    company: frm.doc.college
                }
            };
        });
		frm.set_query("cost_center", function() {
            return {
                filters: {
                    company: frm.doc.college
                }
            };
        });
		frm.set_query("hostel_room", function() {
            return {
                filters: {
                    company: frm.doc.college
                }
            };
        });
        frm.set_query("hostel_room", function() {
            return {
                filters: {
                    company: frm.doc.college
                }
            };
        });
		frm.fields_dict["assets"].grid.get_field("asset").get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    hostel: frm.doc.hostel_room,

                }
            };
        };
	},
	create_maintenance_application: function (frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.hostel_management.doctype.hostel_maintenance_application.hostel_maintenance_application.make_maintenance_application",
			frm: cur_frm
		})
	},
	applied_by: function (frm) {
		// frappe.throw("hh")
		if (frm.doc.applied_by) {
			frappe.call({
				method: "erpnext.hostel_management.doctype.hostel_maintenance_application.hostel_maintenance_application.get_hostel_room_by_student",
				args: {
					applied_by: frm.doc.applied_by
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value("hostel_room", r.message);
					} else {
						frappe.msgprint("No hostel room found for this student.");
						frm.set_value("hostel_room", "");
					}
				}
			});
		}
		
	}
});

frappe.ui.form.on('Hostel Asset Maintenance', {
	asset: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.asset) {
			frappe.call({
				method: "erpnext.hostel_management.doctype.hostel_maintenance_application.hostel_maintenance_application.get_asset_rate",
				args: {
					asset: row.asset
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, 'rate', r.message);
					} else {
						frappe.model.set_value(cdt, cdn, 'rate', 0);
					}
				}
			});
		}
	}
});

