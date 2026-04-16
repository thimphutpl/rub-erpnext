// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Annual Work Plan", {
	refresh(frm) {
        if (frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__("Make Approved Budget"),
				function () {
					frm.events.make_approved_budget(frm);
				}
			)
		}
        frm.set_query('fyp', function(doc, cdt, cdn) {
			return {
				filters: {
					docstatus: 1
				}
			};
		});
        if(frm.doc.is_capital){
            frm.set_value("is_current", 0)
        }
        if(frm.doc.is_current){
            frm.set_value("is_capital", 0)
            frm.set_value("funding_source", "")
        }
	},
    setup: function(frm) {
        frm.fields_dict["apa_extra_details"].grid.get_field("project_no").get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];

            return {
                filters: {
                    planning_output: row.output_no || ""
                }
            };
        };
        frm.fields_dict["apa_extra_details"].grid.get_field("activity_link").get_query = function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];

            return {
                filters: {
                    project: row.project_no || "",
                    college: frm.doc.colleges || ""
                }
            };
        };
        frm.set_query("colleges", function () {
            return {
                filters: {
                    is_group: 0,
                },
            };
        });
    },
    get_planning_info: function(frm){
        frappe.call({
            method:"erpnext.budget.doctype.five_year_plan_proposal.five_year_plan_proposal.fetch_budgetplan",
            args: {
                    fyp: frm.doc.fyp
                },
                callback: function(r) {
                    if (r.message) {
                        // Clear existing rows first (optional)
                        console.log(r.message)
                        frm.clear_table("apa_details");
                        // r.message should be an array of objects
                        r.message.forEach(function(row) {
                            let child = frm.add_child("apa_details");
                            child.output = row.output
                            child.activities= row.activities
                            child.project = row.project
                            child.activity_link = row.activity_link
                            child.output_no = row.output_si_no
                            child.project_no = row.project_si_no
                            child.is_current = row.is_current
                            child.is_capital = row.is_capital
                            child.funding_source = row.funding_source
                        });
                        frm.refresh_field("apa_details");
                    }
                }
        })
    },
    get_additional_activities: function(frm){
        frappe.call({
            method:"erpnext.budget.doctype.annual_work_plan.annual_work_plan.get_additional_activities",
            args: {
                    from_year: frm.doc.from_year,
                    to_year: frm.doc.to_year,
                    college: frm.doc.colleges
                },
                callback: function(r) {
                    if (r.message) {
                        // Clear existing rows first (optional)
                        console.log(r.message)
                        frm.clear_table("apa_extra_details");
                        // r.message should be an array of objects
                        r.message.forEach(function(row) {
                            let child = frm.add_child("apa_extra_details");
                            child.output = row.output
                            child.activities= row.activities
                            child.project = row.project
                            child.activity_link = row.activity_link
                            child.output_no = row.output_no
                            child.project_no = row.project_no
                            child.is_current = row.is_current
                            child.is_capital = row.is_capital
                            child.funding_source = row.funding_source
                        });
                        frm.refresh_field("apa_extra_details");
                    }
                }
        })
    },
    make_approved_budget: function (frm) {
        frappe.model.open_mapped_doc({
            method: "erpnext.budget.doctype.annual_work_plan.annual_work_plan.make_approved_budget",
            frm: cur_frm
        });
	},
});

frappe.ui.form.on("APA Detail Extra", {
    output_no: function(frm, cdt, cdn) {
        frm.refresh_field("apa_extra_details");
    },
    
    is_current: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.is_current) {
            frappe.model.set_value(cdt, cdn, "is_capital", 0);
            frappe.model.set_value(cdt, cdn, "funding_source", "");
        }
    },

    is_capital: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.is_capital) {
            frappe.model.set_value(cdt, cdn, "is_current", 0);
        }
    }
});