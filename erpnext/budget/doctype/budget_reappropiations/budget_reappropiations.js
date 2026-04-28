// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budget Reappropiations", {
	refresh(frm) {
        if (!frm.doc.appropriation_date) {
            frm.set_value("appropriation_date", frappe.datetime.get_today())
        }
        frm.set_query("from_output", () => {
            return {
                filters: {
                    docstatus: 1,
                },
            };
		});
        frm.set_query("to_output", () => {
            return {
                filters: {
                    docstatus: 1,
                },
            };
		});

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
                    docstatus: 1,
                },
            };
		});
    },
    to_output(frm) {
		frm.set_query("to_project", () => {
            return {
                filters: {
                    planning_output: frm.doc.to_output || '',
                    docstatus: 1,
                },
            };
		});
    },
    from_project(frm) {
        frm.set_query("from_activity", () => {
            return {
                filters: {
                    project: frm.doc.from_project || '',
                }
            };
        });
    },

    to_project(frm) {
        frm.set_query("to_activity", () => {
            return {
                filters: {
                    project: frm.doc.to_project || '',
                }
            };
        });
    },
	from_activity_type: function(frm){
        frm.set_value("from_activity", "")
		if (frm.doc.from_activity_type == "Additional Activities"){
			frm.set_query("from_activity", function() {
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
	to_activity_type: function(frm){
        frm.set_value("to_activity", "")
		if (frm.doc.to_activity_type == "Additional Activities"){
			frm.set_query("to_activity", function() {
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
    from_budget_type(frm) {
        frm.set_value("from_activity", "")
        frm.set_query("from_activity", () => {
            let filters = {
                disabled: 0,
                project: frm.doc.from_project || '',
            };
            if (frm.doc.from_activity_type == "Additional Activities"){
                filters.college = frm.doc.college || '';
                filters.from_year = frm.doc.from_year || '';
                filters.to_year = frm.doc.to_year || '';
            }
            if (frm.doc.from_budget_type === "Current") {
                filters.is_current = 1;
            } else if (frm.doc.from_budget_type === "Capital") {
                filters.is_capital = 1;
            }

            return { filters };
        });
    },

    to_budget_type(frm) {
        frm.set_value("to_activity", "")
        frm.set_query("to_activity", () => {
            let filters = {
                disabled: 0,
                project: frm.doc.to_project || '',
            };
            if (frm.doc.to_activity_type == "Additional Activities"){
                filters.college = frm.doc.college || '';
                filters.from_year = frm.doc.from_year || '';
                filters.to_year = frm.doc.to_year || '';
            }
            if (frm.doc.to_budget_type === "Current") {
                filters.is_current = 1;
            } else if (frm.doc.to_budget_type === "Capital") {
                filters.is_capital = 1;
            }

            return { filters };
        });
    },
    from_activity(frm){
        if (frm.doc.from_activity && frm.doc.from_year && frm.doc.to_year && frm.doc.college) {
            frm.trigger("set_available_balance")
        }
    },
    set_available_balance(frm) {
        if (frm.doc.from_activity && frm.doc.from_year && frm.doc.to_year && frm.doc.college) {
			frappe.call({
                method:"erpnext.budget.doctype.budget_reappropiations.budget_reappropiations.get_availabe_balance",
                args: {
                    from_activity: frm.doc.from_activity,
                    from_activity_type: frm.doc.from_activity_type,
                    from_year: frm.doc.from_year,
                    to_year: frm.doc.to_year,
                    college: frm.doc.college,
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("available_balance", r.message);
                        frm.refresh_field("available_balance");
                    }
                }
            })
		}
    }
});
