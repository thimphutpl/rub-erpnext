// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("APA Target Setup", {
	refresh(frm) {
        frm.set_df_property('outcome_items', 'cannot_add_rows', true);
        frm.set_df_property('outcome_items', 'cannot_delete_rows', true);
        frm.set_df_property('output_items', 'cannot_add_rows', true);
        frm.set_df_property('output_items', 'cannot_delete_rows', true);
        frm.set_df_property('output_extra_items', 'cannot_add_rows', true);
        frm.set_df_property('output_extra_items', 'cannot_delete_rows', true);
        refresh_field('outcome_items');
        refresh_field('output_items');
        refresh_field('output_extra_items');
        frm.set_query("department", function () {
            return {
                filters: {
                    company: "Office of Vice Chancellor",
                    include_in_apa: 1
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
    from_year: function(frm) {
        frm.trigger("get_proposal_details");
        frm.clear_table("output_items");
        frm.refresh_field("output_items");
        frm.clear_table("output_extra_items");
        frm.refresh_field("output_extra_items");
        frm.clear_table("outcome_items");
        frm.refresh_field("outcome_items");
        frm.set_value("department", "");
    },
    to_year: function(frm) {
        frm.trigger("get_proposal_details");
        frm.clear_table("output_items");
        frm.refresh_field("output_items");
        frm.clear_table("output_extra_items");
        frm.refresh_field("output_extra_items");
        frm.clear_table("outcome_items");
        frm.refresh_field("outcome_items");
        frm.set_value("department", "");
    },
    college: function(frm) {
        frm.trigger("get_proposal_details");
        frm.clear_table("output_items");
        frm.refresh_field("output_items");
        frm.clear_table("output_extra_items");
        frm.refresh_field("output_extra_items");
        frm.clear_table("outcome_items");
        frm.refresh_field("outcome_items");
        frm.set_value("department", "");
    },
    department: function(frm) {
        frm.trigger("get_proposal_details");
        frm.clear_table("output_items");
        frm.refresh_field("output_items");
        frm.clear_table("output_extra_items");
        frm.refresh_field("output_extra_items");
        frm.clear_table("outcome_items");
        frm.refresh_field("outcome_items");
    },
    get_proposal_details: function(frm){
        ovc_condition = (frm.doc.college != "Office of Vice Chancellor") || (frm.doc.college == "Office of Vice Chancellor" && frm.doc.department);
        if(frm.doc.from_year && frm.doc.to_year && frm.doc.college && ovc_condition){
            frappe.call({
                method:"erpnext.budget.doctype.apa_target_setup.apa_target_setup.fetch_output_and_outcome",
                args: {
                    from_year: frm.doc.from_year,
                    to_year: frm.doc.to_year,
                    college: frm.doc.college,
                    department: frm.doc.department,
                },
                callback: function(r) {
                    if (r.message.output) {
                        frm.clear_table("output_items");
                        r.message.output.forEach(function(row) {
                            let child = frm.add_child("output_items");
                            child.output = row.output
                            child.activities= row.activities
                            child.project = row.project

                            child.output_no = row.output_no
                            child.project_no = row.project_no
                            child.activity_link = row.activity_link
                            child.unit = row.unit
                            child.weightage = row.weightage
                            child.sub_activity_no = row.sub_activity_no
                            child.sub_activity = row.sub_activity
                        });
    
                        frm.refresh_field("output_items");
                    }
                    if (r.message.output_extra) {
                        frm.clear_table("output_extra_items");
                        r.message.output_extra.forEach(function(row) {
                            let child = frm.add_child("output_extra_items");
                            child.output = row.output
                            child.activities= row.activities
                            child.project = row.project

                            child.output_no = row.output_no
                            child.project_no = row.project_no
                            child.unit = row.unit
                            child.weightage = row.weightage
                            child.sub_activity = row.sub_activity
                            child.sub_activity_link = row.sub_activity_link
                            child.activity_link = row.activity_link
                        });
                        frm.refresh_field("output_extra_items");
                    }
                    if (r.message.outcome && r.message.ignore_colleges) {
                        frm.clear_table("outcome_items");
                        console.log(r.message.output_extra)
                        r.message.outcome.forEach(function(row) {
                            let child = frm.add_child("outcome_items");
                            child.outcome = row.outcome
                            child.unit= row.unit
                            // child.weightage = row.weightage
                        });
                        frm.set_df_property("outcome_items", "hidden", 0);
                        frm.refresh_field("outcome_items");
                    }else{
                        frm.clear_table("outcome_items");
                        frm.set_df_property("outcome_items", "hidden", 1);
                        frm.refresh_field("outcome_items");
                    }
                }
            })
        }
    }
});

// get_proposal_details: async function(frm) {
//     let ovc_condition =
//         (frm.doc.college != "Office of Vice Chancellor") ||
//         (frm.doc.college == "Office of Vice Chancellor" && frm.doc.department);

//     if (!(frm.doc.from_year && frm.doc.to_year && frm.doc.college && ovc_condition)) {
//         return;
//     }

//     const r = await frappe.call({
//         method: "erpnext.budget.doctype.apa_target_setup.apa_target_setup.fetch_output_and_outcome",
//         args: {
//             from_year: frm.doc.from_year,
//             to_year: frm.doc.to_year,
//             college: frm.doc.college,
//             department: frm.doc.department,
//         }
//     });

//     if (!r.message) return;

//     // Output Items
//     if (r.message.output) {
//         frm.clear_table("output_items");

//         for (const row of r.message.output) {
//             let child = frm.add_child("output_items");

//             child.output = row.output;
//             child.activities = row.activities;
//             child.project = row.project;
//             child.output_no = row.output_no;
//             child.project_no = row.project_no;
//             child.activity_link = row.activity_link;
//             child.unit = row.unit;
//             child.weightage = row.weightage;
//             child.sub_activity_no = row.sub_activity_no;
//             child.sub_activity = row.sub_activity;

//             // Fetch activity weightage details
//             const response = await frappe.call({
//                 method: "erpnext.budget.doctype.apa_target_setup.apa_target_setup.get_activity_weightage",
//                 args: {
//                     from_year: frm.doc.from_year,
//                     to_year: frm.doc.to_year,
//                     college: frm.doc.college,
//                     activity_link: row.activity_link,
//                     sub_activity_no: row.sub_activity_no
//                 }
//             });

//             const details = response.message?.output_category_items || [];

//             let html = `
//                 <table class="table table-bordered">
//                     <thead>
//                         <tr>
//                             <th>Category</th>
//                             <th>Max</th>
//                             <th>Min</th>
//                             <th>Grade</th>
//                             <th>Score</th>
//                         </tr>
//                     </thead>
//                     <tbody>
//                         ${details.map(item => `
//                             <tr>
//                                 <td>${frappe.utils.escape_html(String(item.category ?? ""))}</td>
//                                 <td>${frappe.utils.escape_html(String(item.max ?? ""))}</td>
//                                 <td>${frappe.utils.escape_html(String(item.min ?? ""))}</td>
//                                 <td>${frappe.utils.escape_html(String(item.grade ?? ""))}</td>
//                                 <td>${frappe.utils.escape_html(String(item.score ?? ""))}</td>
//                             </tr>
//                         `).join("")}
//                     </tbody>
//                 </table>
//             `;

//             // HTML field on the parent form
//             frm.fields_dict.activty_weightage.$wrapper.html(
//                 details.length ? html : "<p>No weightage details found.</p>"
//             );
//         }

//         frm.refresh_field("output_items");
//     }

//     // Extra Output Items
//     if (r.message.output_extra) {
//         frm.clear_table("output_extra_items");

//         r.message.output_extra.forEach(row => {
//             let child = frm.add_child("output_extra_items");

//             child.output = row.output;
//             child.activities = row.activities;
//             child.project = row.project;
//             child.output_no = row.output_no;
//             child.project_no = row.project_no;
//             child.unit = row.unit;
//             child.weightage = row.weightage;
//             child.sub_activity = row.sub_activity;
//             child.sub_activity_link = row.sub_activity_link;
//             child.activity_link = row.activity_link;
//         });

//         frm.refresh_field("output_extra_items");
//     }

//     // Outcome Items
//     if (r.message.outcome && r.message.ignore_colleges) {
//         frm.clear_table("outcome_items");

//         r.message.outcome.forEach(row => {
//             let child = frm.add_child("outcome_items");
//             child.outcome = row.outcome;
//             child.unit = row.unit;
//         });

//         frm.set_df_property("outcome_items", "hidden", 0);
//         frm.refresh_field("outcome_items");
//     } else {
//         frm.clear_table("outcome_items");
//         frm.set_df_property("outcome_items", "hidden", 1);
//         frm.refresh_field("outcome_items");
//     }
// }