// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Annual Performance Agreement", {
	refresh(frm) {
        if (!frm.is_new() && !frm.doc.fyp_copies) {
            frm.add_custom_button(
                __('Apply APA to Other Colleges'),
                function () {
                    frappe.call({
                        method: "erpnext.budget.doctype.annual_performance_agreement.annual_performance_agreement.create_apa_for_subsidiaries",
                        args: {
                            apa_name: frm.doc.name
                        },
                        freeze: true,
                        freeze_message: __('Creating APA copies...'),
                        callback: function (r) {
                            if (r.message && r.message.status === "success") {
                                frappe.msgprint(
                                    `${r.message.created_apa_count} APA copies successfully created`
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
    }
});
