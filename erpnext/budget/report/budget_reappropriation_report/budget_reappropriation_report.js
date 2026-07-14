// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Budget Reappropriation Report"] = {
	filters: [
		{
			fieldname: "college",
			label: __("College"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			get_query: function() {
				return {
					filters: {
						is_group: 0
					}
				};
			},
			on_change: function(query_report) {
				query_report.set_filter_value("from_cost_center", "");
				query_report.set_filter_value("to_cost_center", "");
                query_report.set_filter_value("from_activity", "");
                query_report.set_filter_value("from_activity_type", "");
                query_report.set_filter_value("to_activity", "");
                query_report.set_filter_value("to_activity_type", "");
				query_report.refresh();
			}
		},
		{
			fieldname: "from_year",
			label: __("From Year"),
			fieldtype: "Link",
			options: "Budget Year",
			reqd: 1,
			on_change: function(query_report) {
                let from_year = query_report.get_filter_value("from_year");
                if (!from_year) {
					query_report.set_filter_value(
						"from_date",
						""
					);
					return;
                }
				let from_date = `${from_year}-07-01`;
				query_report.set_filter_value(
					"from_date",
					from_date
				);
				query_report.refresh();
            }
		},
		{
			fieldname: "to_year",
			label: __("To Year"),
			fieldtype: "Link",
			options: "Budget Year",
			reqd: 1,
			on_change: function(query_report) {
                let to_year = query_report.get_filter_value("to_year");
                if (!to_year) {
					query_report.set_filter_value(
						"to_date",
						""
					);
					return;
                }
				let to_date = `${to_year}-06-30`;
				query_report.set_filter_value(
					"to_date",
					to_date
				);
				query_report.refresh();
            }
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "from_cost_center",
			label: __("From Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
			get_query: function() {
				let college = frappe.query_report.get_filter_value("college");
		
				return {
					filters: {
						company: college
					}
				};
			}
		},
		{
			fieldname: "to_cost_center",
			label: __("To Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
			get_query: function() {
				let college = frappe.query_report.get_filter_value("college");
		
				return {
					filters: {
						company: college
					}
				};
			}
		},
		{
            fieldname: "from_activity_type",
            label: __("From Activity Type"),
            fieldtype: "Select",
            options: ["", "Planning Activities", "Additional Activities"],
            on_change: function(query_report) {
                let from_activity_type = query_report.get_filter_value("from_activity_type");
                let college = query_report.get_filter_value("college");
        
                frappe.call({
                    method: "erpnext.budget.report.budgeting_consumption.budgeting_consumption.get_activity_list",
                    args: {
                        activity_type: from_activity_type,
                        college: college
                    },
                    callback: function(r) {
                        let activity_filter = query_report.get_filter("from_activity");
        
                        activity_filter.df.options = [
                            ""
                        ].concat(
                            (r.message || []).map(row => row.name)
                        );
        
                        activity_filter.refresh();
        
                        query_report.set_filter_value("from_activity", "");
                    }
                });
                query_report.refresh();
            }
        },
        {
            fieldname: "from_activity",
            label: __("From Activity"),
            fieldtype: "Select",
            options: [],
        },
		{
            fieldname: "to_activity_type",
            label: __("To Activity Type"),
            fieldtype: "Select",
            options: ["", "Planning Activities", "Additional Activities"],
            on_change: function(query_report) {
                let to_activity_type = query_report.get_filter_value("to_activity_type");
                let college = query_report.get_filter_value("college");
        
                frappe.call({
                    method: "erpnext.budget.report.budgeting_consumption.budgeting_consumption.get_activity_list",
                    args: {
                        activity_type: to_activity_type,
                        college: college
                    },
                    callback: function(r) {
                        let activity_filter = query_report.get_filter("to_activity");
        
                        activity_filter.df.options = [
                            ""
                        ].concat(
                            (r.message || []).map(row => row.name)
                        );
        
                        activity_filter.refresh();
        
                        query_report.set_filter_value("to_activity", "");
                    }
                });
                query_report.refresh();
            }
        },
        {
            fieldname: "to_activity",
            label: __("To Activity"),
            fieldtype: "Select",
            options: [],
        }
	],
}