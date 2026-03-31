// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings["Case Tracking System"] = {
	add_fields: [
		"status",
	],
	get_indicator: function (doc) {
		const status_colors = {
			"Draft": "red",
			"Returned": "red",
			"Closed": "green",
			"Appealed": "orange",
			"Under Review": "orange",
		};
		return [__(doc.status), status_colors[doc.status], "status,=," + doc.status];
	},
	right_column: "grand_total",
};