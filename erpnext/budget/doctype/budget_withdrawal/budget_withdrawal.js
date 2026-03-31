// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budget Withdrawal", {
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
    budget_type(frm) {
		frm.set_query("budget_activity", () => {
            if (frm.doc.budget_type == "Current"){
                return {
                    filters: {
                        is_current: 1,
                    },
                };
            }else if (frm.doc.budget_type == "Capital"){
                return {
                    filters: {
                        is_capital: 1,
                    },
                };
            }else {
                return { filters };
            }
		});
    },
});
