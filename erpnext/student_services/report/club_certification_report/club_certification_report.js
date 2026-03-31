// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Club Certification Report"] = {
	"filters": [
		{
			"fieldname": "club",
			"label": __("Club"),
			"fieldtype": "Link",
			"options": "Club",
			"width": "100px",
			"reqd": 1,  // Make club filter required
			"mandatory": 1  // Make it mandatory
		},
		{
			"fieldname": "college",
			"label": __("College"),
			"fieldtype": "Link",
			"options": "Company",
			
			"width": "100px"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "100px"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "100px"
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		// Highlight rows where years_difference is greater than minimum_year_required
		if (column.fieldname == "years_difference" && data) {
			if (data.years_difference > data.minimum_year_required) {
				value = "<span style='color: green; font-weight: bold;'>" + value + "</span>";
			} else if (data.years_difference == data.minimum_year_required) {
				value = "<span style='color: orange;'>" + value + "</span>";
			}
		}
		
		// Highlight club name
		if (column.fieldname == "club_name" && data) {
			value = "<span style='font-weight: bold;'>" + value + "</span>";
		}
		
		return value;
	},
	
	"onload": function(report) {
		// Add custom buttons or actions if needed
		console.log("Report loaded");
		
		// Add export button functionality
		report.page.add_inner_button(__("Export to Excel"), function() {
			report.export_report("xlsx");
		});
		
		report.page.add_inner_button(__("Export to CSV"), function() {
			report.export_report("csv");
		});
		
		// Optionally set a default club (if needed)
		// frappe.db.get_single_value("Your Settings", "default_club").then(club => {
		//     report.set_filter_value("club", club);
		//     report.refresh();
		// });
	},
	
	"refresh": function(report) {
		// Show message if club is not selected
		if (!report.filters || !report.filters.club) {
			frappe.show_alert({
				message: __("Please select a club to view the report"),
				indicator: "orange"
			}, 5);
		}
	}
};
