// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Five Year Plan", {
	refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(
                __('Make Annual Work Plan'),
                function () {
                    frappe.call({
                        method: "erpnext.budget.doctype.five_year_plan.five_year_plan.create_awp_for_subsidiaries",
                        args: {
                            fyp_name: frm.doc.name
                        },
                        freeze: true,
                        freeze_message: __('Creating AWP copies...'),
                        callback: function (r) {
                            if (r.message && r.message.status === "success") {
                                if (r.message.created_fyp_count == 0){
                                    frappe.msgprint(
                                        `Annual Work Plan already created for all colleges`
                                    );
                                }
                                else{
                                    frappe.msgprint(
                                        `${r.message.created_fyp_count} AWP copies successfully created`
                                    );
                                }
                                frm.reload_doc();
                            }
                        }
                    });
                },
                __('Actions')
            );
        }
	},

    get_proposal_details: function(frm){
        frappe.call({
            method:"erpnext.budget.doctype.five_year_plan.five_year_plan.fetch_budgetplan",
            args: {
                    from_year: frm.doc.from_year,
                    to_year: frm.doc.to_year
                },
                callback: function(r) {
                    if (r.message) {
                        // Clear existing rows first (optional)
                        console.log(r.message)
                        frm.clear_table("items");
    
                        // r.message should be an array of objects
                        r.message.forEach(function(row) {
                            let child = frm.add_child("items");
                            child.output = row.output
                            child.activities= row.activities
                            child.project = row.project

                            child.output_no = row.output_si_no
                            child.project_no = row.project_si_no
                            child.activity_link = row.activity_link
                            child.proposed_budget = row.amount
                            child.approved_budget = row.amount
                            child.is_current = row.is_current
                            child.is_capital = row.is_capital
                            // child.competency = row.competency_item;
                            // child.description = row.description;
                        });
    
                        // Refresh the table to show the new data
                        frm.refresh_field("items");
                    }
                }
        })
    }
    // get_proposal_details: function(frm){
	//     cur_frm.clear_table("items");
	//     cur_frm.refresh_fields("items");
    //     if(frm.doc.from_year && frm.doc.to_year && frm.doc.rub_strategic_plan){
    //         frappe.call({
    //             method:"erpnext.budget.doctype.five_year_plan.five_year_plan.get_fyp_proposal",
    //             args: {
    //                     rub_strategic_plan: frm.doc.rub_strategic_plan,
    //                     from_year: frm.doc.from_year,
    //                     to_year: frm.doc.to_year,
    //                 },
    //                 callback: function(r) {
    //                     if(r.message) {
    //                         cur_frm.clear_table("items");
    //                         r.message.forEach(function(fyp_proposal) {
    //                             var row = frappe.model.add_child(cur_frm.doc, "Five Year Plan Items", "items");
    //                             row.five_year_plan_proposal = fyp_proposal['name']
    //                             row.college = fyp_proposal['colleges']
    //                             row.proposed_budget = fyp_proposal['total_proposed_budget']
    //                             refresh_field("items");
    //                         });
    //                     }
    //                     cur_frm.refresh_fields("items");
    //                 },
    //             freeze: true,
    //             freeze_message: '<span style="color:white; background-color: red; padding: 10px 50px; border-radius: 5px;">Fetching FYP Proposal...</span>',
    //         })
    //     }
    // },
});
