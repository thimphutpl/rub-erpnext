// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Supplementary Budgets", {
	refresh(frm) {
        if (!frm.doc.posting_date) {
            frm.set_value("posting_date", frappe.datetime.get_today())
        }
	},
    setup(frm) {
        frm.set_query("college", function () {
            return {
                filters: {
                    is_group: 0,
                },
            };
        });
    },
    budget_output(frm) {
		frm.set_query("budget_project", () => {
            return {
                filters: {
                    planning_output: frm.doc.budget_output || '',
                },
            };
		});
    },
    budget_project(frm) {
		frm.set_query("budget_activity", () => {
            return {
                filters: {
                    project: frm.doc.budget_project || '',
                },
            };
		});
    },
    
	budget_activity_type: function(frm){
        frm.set_value("budget_activity", "")
		if (frm.doc.budget_activity_type == "Additional Activities"){
			frm.set_query("budget_activity", function() {
                if (!frm.doc.college || !frm.doc.from_year || !frm.doc.to_year) {
                    return {
                        filters: {
                            name: ["=", ""]  // Forces no results
                        }
                    };
                }
				return {
					filters: {
						college: frm.doc.college || '',
						from_year: frm.doc.from_year || '',
						to_year: frm.doc.to_year || '',
					}
				}
			});
		}
	},
    budget_type(frm) {
        frm.set_value("budget_activity", "")
        frm.set_query("budget_activity", () => {
            let filters = {
                disabled: 0,
                project: frm.doc.budget_project || ''
            };
            if (frm.doc.budget_activity_type == "Additional Activities"){
                filters.college = frm.doc.college || '';
                filters.from_year = frm.doc.from_year || '';
                filters.to_year = frm.doc.to_year || '';
            }
            if (frm.doc.budget_type === "Current") {
                filters.is_current = 1;
            }else if (frm.doc.budget_type === "Capital") {
                filters.is_capital = 1;
            }

            return { filters };
        });
    },
});
