// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Maintenance Report", {
	refresh(frm) {
		if (frm.doc.docstatus == 1) {
            if (frm.doc.expenses_borne_by == "Student") {
                frm.add_custom_button(__("Journal Entry"), function() {
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
            }

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
		// Add status update button only if document is submitted and not completed
        if (frm.doc.docstatus === 1 && frm.doc.maintenance_status !== "Completed") {
            frm.add_custom_button(__('Mark as Completed'), function() {
                mark_maintenance_completed(frm);
            }, __("Status"));
        }
        
        // Set status indicator
        set_status_indicator(frm);
        
        // Make status field read-only if document is draft
        if (frm.doc.docstatus === 0) {
            frm.set_df_property('maintenance_status', 'read_only', 0);
            frm.set_df_property('maintenance_status', 'description', __('Status will be set to "On Going" when submitted'));
        } else {
            frm.set_df_property('maintenance_status', 'read_only', 0);
        }
    },
    
    maintenance_status: function(frm) {
        set_status_indicator(frm);
        
        // Show alert when status changes
        if (frm.doc.maintenance_status === "Completed") {
            frappe.show_alert({
                message: __('Maintenance marked as Completed'),
                indicator: 'green'
            }, 5);
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
	},
	get_indicator: function(doc) {

        if (doc.maintenance_status === "Completed") {
            return [__("Completed"), "green", "maintenance_status,=,Completed"];
        }

        if (doc.maintenance_status === "On Going") {
            return [__("On Going"), "orange", "maintenance_status,=,On Going"];
        }

        // fallback
        if (doc.docstatus === 0) {
            return [__("Draft"), "red"];
        }

        if (doc.docstatus === 2) {
            return [__("Cancelled"), "grey"];
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

function mark_maintenance_completed(frm) {
    frappe.confirm(
        __('Are you sure you want to mark this maintenance as Completed?'),
        function() {
            frappe.call({
                method: "erpnext.hostel_management.doctype.hostel_maintenance_report.hostel_maintenance_report.update_maintenance_status",
                args: {
                    report_name: frm.doc.name,
                    new_status: "Completed"
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.msgprint({
                            title: __('Success'),
                            message: r.message.message,
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    }
                }
            });
        }
    );
}

// function set_status_indicator(frm) {
//     // Set status indicator on the form
//     if (frm.doc.maintenance_status === "Completed") {
//         frm.page.set_indicator(__('Completed'), 'green');
//     } else if (frm.doc.maintenance_status === "On Going") {
//         frm.page.set_indicator(__('On Going'), 'orange');
//     } else if (frm.doc.docstatus === 0) {
//         frm.page.set_indicator(__('Draft'), 'red');
//     } else {
//         frm.page.set_indicator(__('Completed'), 'blue');
//     }
// }

function set_status_indicator(frm) {
    if (frm.doc.status === "Completed") {
        frm.page.set_indicator(__('Completed'), 'green');
    } else if (frm.doc.status === "On Going") {
        frm.page.set_indicator(__('On Going'), 'orange');
    } else if (frm.doc.status === "Cancelled") {
        frm.page.set_indicator(__('Cancelled'), 'red');
    }
}
