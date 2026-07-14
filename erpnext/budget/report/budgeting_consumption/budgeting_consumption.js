// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Budgeting Consumption"] = {
	"filters": [
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
                query_report.set_filter_value("activity", "");
                query_report.set_filter_value("activity_type", "");
                query_report.set_filter_value("cost_center", "");
				query_report.refresh();
			}
        },
		{
            fieldname: "from_year",
            label: __("From Year"),
            fieldtype: "Link",
            options: "Budget Year",
            reqd: 1
        },
        {
            fieldname: "to_year",
            label: __("To Year"),
            fieldtype: "Link",
            options: "Budget Year",
            reqd: 1
        },
        {
            fieldname: "cost_center",
            label: __("Cost Center"),
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
            fieldname: "activity_type",
            label: __("Activity Type"),
            fieldtype: "Select",
            options: ["", "Planning Activities", "Additional Activities"],
            on_change: function(query_report) {
                let activity_type = query_report.get_filter_value("activity_type");
                let college = query_report.get_filter_value("college");
        
                frappe.call({
                    method: "erpnext.budget.report.budgeting_consumption.budgeting_consumption.get_activity_list",
                    args: {
                        activity_type: activity_type,
                        college: college
                    },
                    callback: function(r) {
                        let activity_filter = query_report.get_filter("activity");
        
                        activity_filter.df.options = [
                            ""
                        ].concat(
                            (r.message || []).map(row => row.name)
                        );
        
                        activity_filter.refresh();
        
                        query_report.set_filter_value("activity", "");
                    }
                });
                query_report.refresh();
            }
        },
        {
            fieldname: "activity",
            label: __("Activity"),
            fieldtype: "Select",
            options: [],
        },
        // {
        //     fieldname: "budget_type",
        //     label: __("Budget Type"),
        //     fieldtype: "Select",
        //     options: ["", "Current", "Capital"],
        // }
	],
};
