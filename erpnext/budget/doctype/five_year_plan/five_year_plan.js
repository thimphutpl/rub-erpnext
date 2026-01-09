// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Five Year Plan", {
	refresh(frm) {
        if (!frm.is_new() && !frm.doc.fyp_copies) {
            frm.add_custom_button(
                __('Apply FYP to Other Colleges'),
                function () {
                    frappe.call({
                        method: "erpnext.budget.doctype.five_year_plan.five_year_plan.create_fyp_for_subsidiaries",
                        args: {
                            fyp_name: frm.doc.name
                        },
                        freeze: true,
                        freeze_message: __('Creating FYP copies...'),
                        callback: function (r) {
                            if (r.message && r.message.status === "success") {
                                frappe.msgprint(
                                    `${r.message.created_fyp_count} FYP copies successfully created`
                                );
                                frm.reload_doc();
                            }
                        }
                    });
                },
                __('Actions')
            );
        }
    

	},

    get_planning_info: function(frm){
        frappe.call({
            method:"erpnext.budget.doctype.five_year_plan.five_year_plan.fetch_budgetplan",
            
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
