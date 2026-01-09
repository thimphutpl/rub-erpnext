// Copyright (c) 2025, Frappe Technologies Pvt. Ltd.
// For license information, please see license.txt

frappe.ui.form.on("Item Sub Group", {
	refresh: function (frm) {
		// Filter for asset_sub_category
		frm.set_query("asset_sub_category", function () {
			return {
				filters: {
					asset_category: frm.doc.asset_category,
				},
			};
		});

		// Filter for item_sub_group
		frm.set_query("item_sub_group", function () {
			return {
				filters: {
					item_group: frm.doc.item_group, // Make sure item_group exists in the DocType
				},
			};
		});
		frm.set_query("expense_head", function () {
			return {
				filters: {
					root_type: "Expense" // Make sure item_group exists in the DocType
				},
			};
		});
	}
});
