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
                            // child.competency = row.competency_item;
                            // child.description = row.description;
                        });
    
                        // Refresh the table to show the new data
                        frm.refresh_field("apa_details");
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
