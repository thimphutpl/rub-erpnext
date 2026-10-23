// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("APA Mid Term Activity Change Request", {
    refresh(frm) {
        // frm.set_df_property('outcome_items', 'cannot_add_rows', true);
        // frm.set_df_property('outcome_items', 'cannot_delete_rows', true);
        // // frm.set_df_property('output_items', 'cannot_add_rows', true);
        // frm.set_df_property('output_items', 'cannot_delete_rows', true);
        // // frm.set_df_property('output_extra_items', 'cannot_add_rows', true);
        // frm.set_df_property('output_extra_items', 'cannot_delete_rows', true);
        // refresh_field('outcome_items');
        // refresh_field('output_items');
        // refresh_field('output_extra_items');
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
        frm.set_query("sub_activity_no", "output_items", function (doc, cdt, cdn) {
            const row = locals[cdt][cdn];

            return {
                filters: {
                    activity: row.activity_link,
                    college: doc.college
                }
            };
        });
        frm.set_query("activity_link", "output_extra_items", function (doc, cdt, cdn) {
            const row = locals[cdt][cdn];

            return {
                filters: {
                    college: doc.college
                }
            };
        });
        frm.set_query("sub_activity_link", "output_extra_items", function (doc, cdt, cdn) {
            const row = locals[cdt][cdn];

            return {
                filters: {
                    activity: row.activity_link,
                    college: row.college
                }
            };
        });
    },
    from_year: function(frm) {
        frm.trigger("get_target_setup_details");
        frm.clear_table("output_items");
        frm.refresh_field("output_items");
        frm.clear_table("output_extra_items");
        frm.refresh_field("output_extra_items");
        frm.clear_table("outcome_items");
        frm.refresh_field("outcome_items");
    },
    to_year: function(frm) {
        frm.trigger("get_target_setup_details");
        frm.clear_table("output_items");
        frm.refresh_field("output_items");
        frm.clear_table("output_extra_items");
        frm.refresh_field("output_extra_items");
        frm.clear_table("outcome_items");
        frm.refresh_field("outcome_items");
    },
    college: function(frm) {
        frm.trigger("get_target_setup_details");
        frm.clear_table("output_items");
        frm.refresh_field("output_items");
        frm.clear_table("output_extra_items");
        frm.refresh_field("output_extra_items");
        frm.clear_table("outcome_items");
        frm.refresh_field("outcome_items");
    },
    department: function(frm) {
        frm.trigger("get_target_setup_details");
        frm.clear_table("output_items");
        frm.refresh_field("output_items");
        frm.clear_table("output_extra_items");
        frm.refresh_field("output_extra_items");
        frm.clear_table("outcome_items");
        frm.refresh_field("outcome_items");
    },
    get_target_setup_details: function(frm){
        ovc_condition = (frm.doc.college != "Office of Vice Chancellor") || (frm.doc.college == "Office of Vice Chancellor" && frm.doc.department);
        if(frm.doc.from_year && frm.doc.to_year && frm.doc.college && ovc_condition){
            frappe.call({
                method:"erpnext.budget.doctype.apa_mid_term_activity_change_request.apa_mid_term_activity_change_request.get_target_setup_details",
                args: {
                    from_year: frm.doc.from_year,
                    to_year: frm.doc.to_year,
                    college: frm.doc.college,
                    department: frm.doc.department
                },
                callback: function(r) {
                    if (r.message.output) {
                        console.log(r.message.output)
                        frm.clear_table("output_items");

                        r.message.output.forEach(function(row) {
                            let child = frm.add_child("output_items");
                            child.output = row.output
                            child.activities= row.activities
                            child.project = row.project
                            child.output_no = row.output_no
                            child.project_no = row.project_no
                            child.activity_link = row.activity_link
                            child.sub_activity_no = row.sub_activity_no
                            child.sub_activity = row.sub_activity
                            child.weightage = row.weightage
                            child.unit = row.unit
                            child.target = row.target
                        });
    
                        frm.refresh_field("output_items");
                    }
                    if (r.message.output_extra) {
                        console.log(r.message.output_extra)
                        frm.clear_table("output_extra_items");

                        r.message.output_extra.forEach(function(row) {
                            let child = frm.add_child("output_extra_items");
                            child.output = row.output
                            child.activities= row.activities
                            child.project = row.project
                            child.output_no = row.output_no
                            child.project_no = row.project_no
                            child.sub_activity = row.sub_activity
                            child.sub_activity_link = row.sub_activity_link
                            child.activity_link = row.activity_link
                            child.weightage = row.weightage
                            child.unit = row.unit
                            child.target = row.target
                        });
    
                        frm.refresh_field("output_extra_items");
                    }
                    if (r.message.outcome && !(frm.doc.college in r.message.ignore_colleges)) {
                        frm.set_df_property("outcome_items", "hidden", 0);
                        console.log(r.message.outcome)
                        frm.clear_table("outcome_items");
                        
                        r.message.outcome.forEach(function(row) {
                            let child = frm.add_child("outcome_items");
                            child.outcome = row.outcome
                            child.unit = row.unit
                            child.target = row.target
                        });
                        frm.refresh_field("outcome_items");
                    }else{
                        frm.set_df_property("outcome_items", "hidden", 1);
                        frm.refresh_field("outcome_items");
                    }
                }
            })
        }
    }
});

frappe.ui.form.on("Mid Term CR Outcome Item", {
    outcome_items_add(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, {is_new_activity: 1, drop_activity: 0});
    },
    is_new_activity(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "drop_activity", 0);
    },
    drop_activity(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "is_new_activity", 0);
    },
    outcome(frm, cdt, cdn){
        const row = locals[cdt][cdn];
        if(frm.doc.from_year && frm.doc.to_year && frm.doc.college && row.outcome){
            frappe.call({
                method:"erpnext.budget.doctype.apa_mid_term_activity_change_request.apa_mid_term_activity_change_request.get_outcome_unit",
                args: {
                    from_year: frm.doc.from_year,
                    to_year: frm.doc.to_year,
                    college: frm.doc.college,
                    outcome: row.outcome,
                },
                callback: function(r) {
                    frappe.model.set_value(cdt, cdn, "unit", r.message || "");
                }
            })
        }else{
            frappe.model.set_value(cdt, cdn, "unit", "");
        }
    },
});
frappe.ui.form.on("Mid Term CR Output Item", {
    output_items_add(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, {is_new_activity: 1, drop_activity: 0});
    },
    is_new_activity(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "drop_activity", 0);
    },
    drop_activity(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "is_new_activity", 0);
    },
    activity_link(frm, cdt, cdn){
        const row = locals[cdt][cdn];
        if(frm.doc.from_year && frm.doc.to_year && frm.doc.college && row.activity_link){
            frappe.call({
                method:"erpnext.budget.doctype.apa_mid_term_activity_change_request.apa_mid_term_activity_change_request.get_output_unit",
                args: {
                    from_year: frm.doc.from_year,
                    to_year: frm.doc.to_year,
                    college: frm.doc.college,
                    activity_link: row.activity_link,
                },
                callback: function(r) {
                    frappe.model.set_value(cdt, cdn, "unit", r.message || "");
                }
            })
        }else{
            frappe.model.set_value(cdt, cdn, "unit", "");
        }
    },
    sub_activity_no(frm, cdt, cdn){
        const row = locals[cdt][cdn];
        if(frm.doc.from_year && frm.doc.to_year && frm.doc.college && row.activity_link && row.sub_activity_no){
            frappe.call({
                method:"erpnext.budget.doctype.apa_mid_term_activity_change_request.apa_mid_term_activity_change_request.get_output_unit",
                args: {
                    from_year: frm.doc.from_year,
                    to_year: frm.doc.to_year,
                    college: frm.doc.college,
                    activity_link: row.activity_link,
                    sub_activity_no: row.sub_activity_no,
                },
                callback: function(r) {
                    frappe.model.set_value(cdt, cdn, "unit", r.message || "");
                }
            })
        }
        else{
            frappe.model.set_value(cdt, cdn, "unit", "");
        }
    }
});
frappe.ui.form.on("Mid Term CR Output Extra Item", {
    output_extra_items_add(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, {is_new_activity: 1, drop_activity: 0});
    },
    is_new_activity(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "drop_activity", 0);
    },
    drop_activity(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "is_new_activity", 0);
    },
    activity_link(frm, cdt, cdn){
        const row = locals[cdt][cdn];
        if(frm.doc.from_year && frm.doc.to_year && frm.doc.college && row.activity_link){
            frappe.call({
                method:"erpnext.budget.doctype.apa_mid_term_activity_change_request.apa_mid_term_activity_change_request.get_output_extra_unit",
                args: {
                    from_year: frm.doc.from_year,
                    to_year: frm.doc.to_year,
                    college: frm.doc.college,
                    activity_link: row.activity_link,
                },
                callback: function(r) {
                    frappe.model.set_value(cdt, cdn, "unit", r.message || "");
                }
            })
        }else{
            frappe.model.set_value(cdt, cdn, "unit", "");
        }
    },
    sub_activity_link(frm, cdt, cdn){
        const row = locals[cdt][cdn];
        if(frm.doc.from_year && frm.doc.to_year && frm.doc.college && row.activity_link && row.sub_activity_link){
            frappe.call({
                method:"erpnext.budget.doctype.apa_mid_term_activity_change_request.apa_mid_term_activity_change_request.get_output_extra_unit",
                args: {
                    from_year: frm.doc.from_year,
                    to_year: frm.doc.to_year,
                    college: frm.doc.college,
                    activity_link: row.activity_link,
                    sub_activity_link: row.sub_activity_link,
                },
                callback: function(r) {
                    frappe.model.set_value(cdt, cdn, "unit", r.message || "");
                }
            })
        }
        else{
            frappe.model.set_value(cdt, cdn, "unit", "");
        }
    }
});