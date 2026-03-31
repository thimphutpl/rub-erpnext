// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budget Reappropiations", {
	refresh(frm) {
        if (!frm.doc.appropriation_date) {
            frm.set_value("appropriation_date", frappe.datetime.get_today())
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
    from_output(frm) {
		frm.set_query("from_project", () => {
            return {
                filters: {
                    planning_output: frm.doc.from_output || '',
                },
            };
		});
    },
    to_output(frm) {
		frm.set_query("to_project", () => {
            return {
                filters: {
                    planning_output: frm.doc.to_output || '',
                },
            };
		});
    },
    from_project(frm) {
        frm.set_query("from_activity", () => {
            return {
                filters: {
                    project: frm.doc.from_project || ''
                }
            };
        });
    },

    to_project(frm) {
        frm.set_query("to_activity", () => {
            return {
                filters: {
                    project: frm.doc.to_project || ''
                }
            };
        });
    },

    from_budget_type(frm) {
        frm.set_query("from_activity", () => {
            let filters = {
                project: frm.doc.from_project || ''
            };

            if (frm.doc.from_budget_type === "Current") {
                filters.is_current = 1;
            } else if (frm.doc.from_budget_type === "Capital") {
                filters.is_capital = 1;
            }

            return { filters };
        });
    },

    to_budget_type(frm) {
        frm.set_query("to_activity", () => {
            let filters = {
                project: frm.doc.to_project || ''
            };

            if (frm.doc.to_budget_type === "Current") {
                filters.is_current = 1;
            } else if (frm.doc.to_budget_type === "Capital") {
                filters.is_capital = 1;
            }

            return { filters };
        });
    }
});
