// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Maintenance Report", {
	refresh(frm) {
		if (frm.doc.docstatus == 1) {
            // if (frm.doc.expenses_borne_by == "Student") {
                frm.add_custom_button(__("Payment Entry"), function() {
                    frappe.call({
                        method: "erpnext.hostel_management.doctype.hostel_maintenance_report.hostel_maintenance_report.make_payment_entry",
                        args: { source_name: frm.doc.name },
                        callback: function(r) {
                            if (r.message) {
                                frappe.model.sync(r.message);
                                frappe.set_route("Form", r.message.doctype, r.message.name);
                            }
                        }
                    });
                }, __("Create"));
            // }

            // if (frm.doc.expenses_borne_by == "College") {
            //     frm.add_custom_button(__("Stock Entry"), function() {
            //         frappe.call({
            //             method: "erpnext.hostel_management.doctype.hostel_maintenance_report.hostel_maintenance_report.make_stock_entry",
            //             args: { source_name: frm.doc.name },
            //             callback: function(r) {
            //                 if (r.message) {
            //                     frappe.model.sync(r.message);
            //                     frappe.set_route("Form", r.message.doctype, r.message.name);
            //                 }
            //             }
            //         });
            //     }, __("Create"));
            // }
        }
        if (frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__("Stock Ledger"), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company
				};
				frappe.set_route("query-report", "Stock Ledger Report");
			}, __("View"));
		
			cur_frm.add_custom_button(__('Accounting Ledger'), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		
		}
        if (frm.is_new()) {
            frm.set_value("posting_date", frappe.datetime.get_today());
            // frm.set_value("posting_time", frappe.datetime.get_today());
        }

	},
    onload: function (frm) {
        if (frm.is_new()) {
            frm.set_value("posting_date", frappe.datetime.get_today());
            // frm.set_value("posting_time", frappe.datetime.get_today());
        }
    },
    // onload_post_render(frm) {
	// 	update_child_table_columns(frm);
	// },
	// refresh(frm) {
	// 	update_child_table_columns(frm);
	// }
	cost_center: function(frm) {
		if (frm.doc.cost_center) {
			frappe.call({
				method: "erpnext.hostel_management.doctype.hostel_maintenance_report.hostel_maintenance_report.get_warehouse_by_cost_center",
				args: {
					cost_center: frm.doc.cost_center
				},
				callback: function(r) {
					if (r.message) {
						(frm.doc.items || []).forEach(row => {
							frappe.model.set_value(row.doctype, row.name, "warehouse", r.message);
						});
						frm.refresh_field("items");
					}
				}
			});
		}
	}
});

function update_child_table_columns(frm) {
	let grid = frm.get_field("items").grid;

	// Reset column visibility
	const fields = ["asset", "asset_name", "item_code", "item_name"];
	fields.forEach(f => {
		let df = grid.get_field(f);
		if (df) df.df.hidden = 0;
	});

	// Hide columns depending on each row's expense type
	let hide_asset = true;
	let hide_item = true;

	(frm.doc.items || []).forEach(row => {
		if (row.expenses_type === "Asset") hide_item = false;
		if (row.expenses_type === "Stock Item") hide_asset = false;
	});

	// Apply visibility rules
	if (hide_asset) {
		["asset", "asset_name"].forEach(f => {
			let df = grid.get_field(f);
			if (df) df.df.hidden = 1;
		});
	}

	if (hide_item) {
		["item_code", "item_name"].forEach(f => {
			let df = grid.get_field(f);
			if (df) df.df.hidden = 1;
		});
	}

	// Force re-rendering of the grid header and rows
	grid.refresh();
}

frappe.ui.form.on("Hostel Maintenance Item", {
	expenses_type(frm, cdt, cdn) {
		let row = locals[cdt][cdn];

		// Clear irrelevant fields first
		if (row.expenses_type === "Asset") {
			frappe.model.set_value(cdt, cdn, "item_code", "");
			frappe.model.set_value(cdt, cdn, "item_name", "");
		} else if (row.expenses_type === "Stock Item") {
			frappe.model.set_value(cdt, cdn, "asset", "");
			frappe.model.set_value(cdt, cdn, "asset_name", "");
		}

		// Refresh grid columns after selection
		update_child_table_columns(frm);
	},
    item_code: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.item_code) {
			frappe.call({
				method: "erpnext.hostel_management.doctype.hostel_maintenance_report.hostel_maintenance_report.get_asset_rate",
				args: {
					item_code: row.item_code
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
	},
});