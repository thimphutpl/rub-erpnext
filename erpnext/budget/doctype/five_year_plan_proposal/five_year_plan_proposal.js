// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Five Year Plan Proposal", {
	refresh(frm) {
        
	},
    setup(frm) {
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
            
            // args: {
            //         name: frm.doc.name,
            //         pms_group:frm.doc.pms_group
            //     },
                callback: function(r) {
                    if (r.message) {
                        // Clear existing rows first (optional)
                        console.log(r.message)
                        frm.clear_table("fyp_details");
    
                        // r.message should be an array of objects
                        r.message.forEach(function(row) {
                            let child = frm.add_child("fyp_details");
                            child.output = row.output
                            child.activities= row.activities
                            child.project = row.project
                            child.output_no = row.output_si_no
                            child.project_no = row.project_si_no
                            child.activity_link = row.activity_link
                            child.is_current = row.is_current
                            child.is_capital = row.is_capital
                            // child.competency = row.competency_item;
                            // child.description = row.description;
                        });
    
                        // Refresh the table to show the new data
                        frm.refresh_field("fyp_details");
                    }
                }
        })
    }
});
