// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Output Indicator", {
	refresh(frm) {

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
    get_planning_info: function(frm){
        if (frm.doc.from_year && frm.doc.to_year && frm.doc.college){
            frappe.call({
                method:"erpnext.budget.doctype.output_indicator.output_indicator.fetch_budgetplan",
                args: {
                        from_year: frm.doc.from_year,
                        to_year: frm.doc.to_year,
                        college: frm.doc.college
                    },
                callback: function(r) {
                    if (r.message.approved_budget_items) {
                        // Clear existing rows first (optional)
                        console.log(r.message)
                        frm.clear_table("items");
    
                        // r.message should be an array of objects
                        r.message.approved_budget_items.forEach(function(row) {
                            let child = frm.add_child("items");
                            child.output = row.output
                            child.activities= row.activities
                            child.project = row.project
                            child.output_no = row.output_no
                            child.project_no = row.project_no
                            child.activity_link = row.activity_link
                            child.sub_activity_no = row.sub_activity_no
                            child.sub_activity = row.sub_activity
                            child.unit = row.unit
                            // child.competency = row.competency_item;
                            // child.description = row.description;
                        });
    
                        // Refresh the table to show the new data
                        frm.refresh_field("items");
                    }
                    if (r.message.approved_budget_extra_items) {
                        // Clear existing rows first (optional)
                        console.log(r.message)
                        frm.clear_table("additional_activities");
    
                        // r.message should be an array of objects
                        r.message.approved_budget_extra_items.forEach(function(row) {
                            let child = frm.add_child("additional_activities");
                            child.output = row.output
                            child.activities= row.activities
                            child.project = row.project
    
                            child.output_no = row.output_no
                            child.project_no = row.project_no
                            child.activity_link = row.activity_link
                            child.sub_activity_no = row.sub_activity_no
                            child.sub_activity = row.sub_activity
                            child.unit = row.unit
                        });
    
                        // Refresh the table to show the new data
                        frm.refresh_field("additional_activities");
                    }
                }
            })
        }
    }
});

// frappe.ui.form.on("Output Indicator Item", {
//     sub_activity_no: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         fetch_unit(null, row.sub_activity_no)
//     },
//     activity_link: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         fetch_unit(row.activity_link, null)
//     },
// });
// function fetch_unit(activity_link, sub_activity_no) {
//     frappe.call({
//         method:"erpnext.budget.doctype.output_indicator.output_indicator.fetch_unit",
//         args: {
//             sub_activity_no: sub_activity_no,
//             activity_link: activity_link
//         },
//         callback: function(r) {
//             if (r.message.approved_budget_items) {
//                 // Clear existing rows first (optional)
//                 console.log(r.message)
//                 frm.clear_table("items");

//                 // r.message should be an array of objects
//                 r.message.approved_budget_items.forEach(function(row) {
//                     let child = frm.add_child("items");
//                     child.output = row.output
//                     child.activities= row.activities
//                     child.project = row.project
//                     child.output_no = row.output_no
//                     child.project_no = row.project_no
//                     child.activity_link = row.activity_link
//                     child.sub_activity_no = row.sub_activity_no
//                     child.sub_activity = row.sub_activity
//                     child.unit = row.unit
//                     // child.competency = row.competency_item;
//                     // child.description = row.description;
//                 });

//                 // Refresh the table to show the new data
//                 frm.refresh_field("items");
//             }
//             if (r.message.approved_budget_extra_items) {
//                 // Clear existing rows first (optional)
//                 console.log(r.message)
//                 frm.clear_table("additional_activities");

//                 // r.message should be an array of objects
//                 r.message.approved_budget_extra_items.forEach(function(row) {
//                     let child = frm.add_child("additional_activities");
//                     child.output = row.output
//                     child.activities= row.activities
//                     child.project = row.project

//                     child.output_no = row.output_no
//                     child.project_no = row.project_no
//                     child.activity_link = row.activity_link
//                     child.sub_activity_no = row.sub_activity_no
//                     child.sub_activity = row.sub_activity
//                     child.unit = row.unit
//                 });

//                 // Refresh the table to show the new data
//                 frm.refresh_field("additional_activities");
//             }
//         }
//     })

//     frm.refresh_field("items");
// }