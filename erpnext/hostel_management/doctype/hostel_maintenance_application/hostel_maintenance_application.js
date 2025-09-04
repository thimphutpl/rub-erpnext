// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Maintenance Application", {
	refresh(frm) {
		if (!frm.doc.travel_claim) {
			frm.add_custom_button(__("Hostel Maintenance Report"), function () {
				frm.trigger("create_maintenance_application");
				},
				__("Create")
			);
		}

	},
	create_maintenance_application: function (frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.hostel_management.doctype.hostel_maintenance_application.hostel_maintenance_application.make_maintenance_application",
			frm: cur_frm
		})
	},
});
