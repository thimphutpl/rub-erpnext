// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Planning Output", {
	refresh(frm) {
        if (frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__("Make Planning Project"),
				function () {
					frm.events.make_planning_project(frm);
				}
			)
		}
	},
    make_planning_project: function (frm) {
		frappe.call({
			method: "erpnext.budget.doctype.planning_output.planning_output.make_planning_project",
			args: {
				name: frm.doc.name,
				from_date: frm.doc.from_date,
				to_date: frm.doc.to_date,
			},
			callback: function (r) {
				var doclist = frappe.model.sync(r.message);
				frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
			}
		});
	},
});
