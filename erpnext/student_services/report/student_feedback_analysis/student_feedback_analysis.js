// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Student Feedback Analysis"] = {
	"filters": [
		{
			"fieldname": "feedback_type",
			"label": __("Feedback Type"),
			"fieldtype": "Link",
			"options": "Feedback Type",
			"width": 150
		},
		{
			"fieldname": "college",
			"label": __("College"),
			"fieldtype": "Link",
			"options": "Company",
			"width": 150
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		// Color code for average ratings
		if (column.fieldname === "average_rating") {
			if (value >= 4.0) {
				return `<span style="color: green; font-weight: bold;">${parseFloat(value).toFixed(2)}</span>`;
			} else if (value >= 3.0) {
				return `<span style="color: orange;">${parseFloat(value).toFixed(2)}</span>`;
			} else if (value < 2.0) {
				return `<span style="color: red; font-weight: bold;">${parseFloat(value).toFixed(2)}</span>`;
			}
			return `<span>${parseFloat(value).toFixed(2)}</span>`;
		}
		
		// Highlight high student participation
		if (column.fieldname === "student_count" && value > 50) {
			return `<span style="color: blue; font-weight: bold;">${value}</span>`;
		}
		
		return default_formatter(value, row, column, data);
	},
	
	// Add chart configuration
	"get_chart_data": function(columns, data) {
		if (!data || data.length === 0) {
			return null;
		}
		
		// Prepare data for chart - Top 10 questions by student count
		let sorted_data = [...data].sort((a, b) => b.student_count - a.student_count);
		let top_10 = sorted_data.slice(0, 10);
		
		let labels = top_10.map(d => {
			let question = d.question;
			return question.length > 40 ? question.substring(0, 37) + "..." : question;
		});
		
		let values = top_10.map(d => d.student_count);
		
		return {
			data: {
				labels: labels,
				datasets: [
					{
						name: __("Number of Students"),
						values: values,
						chartType: "bar"
					}
				]
			},
			type: "bar",
			title: __("Top 10 Questions by Student Participation"),
			height: 300,
			colors: ["#4CAF50"]
		};
	},
	
	"onload": function(report) {
		// Add export buttons
		report.page.add_inner_button(__("Export to Excel"), function() {
			report.export_report("xlsx");
		});
		
		report.page.add_inner_button(__("Export to CSV"), function() {
			report.export_report("csv");
		});
	}
};