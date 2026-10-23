// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Annual Performance Assessment OVC", {
	refresh(frm) {
        frm.set_df_property('output_items', 'cannot_add_rows', true);
        frm.set_df_property('output_items', 'cannot_delete_rows', true);
        frm.set_df_property('output_extra_items', 'cannot_add_rows', true);
        frm.set_df_property('output_extra_items', 'cannot_delete_rows', true);
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
    // setup(frm) {
    //     frm.set_query("college", function () {
    //         return {
    //             filters: {
    //                 is_group: 0,
    //                 is_overseeing_company: 0,
    //             },
    //         };
    //     });
    // },
    from_year: function(frm) {
        frm.trigger("fetch_output_and_outcome");
        frm.clear_table("output_items");
        frm.refresh_field("output_items");
        frm.clear_table("output_extra_items");
        frm.refresh_field("output_extra_items");
        frm.clear_table("outcome_items");
        frm.refresh_field("outcome_items");
    },
    to_year: function(frm) {
        frm.trigger("fetch_output_and_outcome");
        frm.clear_table("output_items");
        frm.refresh_field("output_items");
        frm.clear_table("output_extra_items");
        frm.refresh_field("output_extra_items");
        frm.clear_table("outcome_items");
        frm.refresh_field("outcome_items");
    },
    department: function(frm) {
        frm.trigger("fetch_output_and_outcome");
        frm.clear_table("output_items");
        frm.refresh_field("output_items");
        frm.clear_table("output_extra_items");
        frm.refresh_field("output_extra_items");
        frm.clear_table("outcome_items");
        frm.refresh_field("outcome_items");
    },
    fetch_output_and_outcome: function(frm){
        if(frm.doc.from_year && frm.doc.to_year && frm.doc.department){
            frappe.call({
                method:"erpnext.budget.doctype.annual_performance_assessment_ovc.annual_performance_assessment_ovc.fetch_output_and_outcome",
                args: {
                        from_year: frm.doc.from_year,
                        to_year: frm.doc.to_year,
                        college: "Office of Vice Chancellor",
                        department: frm.doc.department,
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
                                child.unit = row.unit
                                child.weightage = row.weightage
                                child.target = row.target
                                child.sub_activity_no = row.sub_activity_no
                                child.sub_activity = row.sub_activity
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
                                child.unit = row.unit
                                child.weightage = row.weightage
                                child.target = row.target
                                child.sub_activity = row.sub_activity
                                child.sub_activity_link = row.sub_activity_link
                                child.activity_link = row.activity_link
                            });
        
                            frm.refresh_field("output_extra_items");
                        }
                        if (r.message.outcome) {
                            console.log(r.message.outcome)
                            frm.clear_table("outcome_items");
                            
                            r.message.outcome.forEach(function(row) {
                                let child = frm.add_child("outcome_items");
                                child.college = row.college
                                child.irt_rating= row.outcome_rating
                            });
        
                            frm.refresh_field("outcome_items");
                        }
                    }
            })
        }
    }
});

frappe.ui.form.on("APA Output Item", {
    raw_rating: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		// if (row.raw_rating) {
			frappe.call({
                method:"erpnext.budget.doctype.annual_performance_assessment_ovc.annual_performance_assessment_ovc.calculate_output_irt_rating",
                args: {
                        raw_rating: row.raw_rating,
                        activity_link: row.activity_link,
                        unit: row.unit,
                        weightage: row.weightage,
                        college: "Office of Vice Chancellor",
                        department: frm.doc.department,
                        from_year: frm.doc.from_year,
                        to_year: frm.doc.to_year,
                        sub_activity_no: row.sub_activity_no,
                    },
                callback: function(r) {
                    if (r.message) {
                        if (r.message.irt_rating && r.message.irt_rating > 0) {
                            frappe.model.set_value(cdt, cdn, "irt_rating", r.message.irt_rating);        
                            frappe.model.set_value(cdt, cdn, "weighted_score", r.message.weighted_score);
                            frappe.model.set_value(cdt, cdn, "category", r.message.category);
                        }else{
                            frappe.model.set_value(cdt, cdn, "irt_rating", "0"); 
                            frappe.model.set_value(cdt, cdn, "weighted_score", 0);
                            frappe.model.set_value(cdt, cdn, "category", "");                                               
                        }
                        if (row.irt_rating > 0){
                            irt_rating(frm, cdt, cdn)

                            // frappe.trigger("irt_rating")
                        }                                  
                        frm.refresh_field("irt_rating");
                        frm.refresh_field("weighted_score");
                        frm.refresh_field("category");
                    }
                }
            })
		// } 
	},
});

frappe.ui.form.on("Annual Performance Extra Item", {
    raw_rating: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		// if (row.raw_rating) {
			frappe.call({
                method:"erpnext.budget.doctype.annual_performance_assessment_ovc.annual_performance_assessment_ovc.calculate_extra_output_irt_rating",
                args: {
                        raw_rating: row.raw_rating,
                        activity_link: row.activity_link,
                        unit: row.unit,
                        weightage: row.weightage,
                        college: "Office of Vice Chancellor",
                        department: frm.doc.department,
                        from_year: frm.doc.from_year,
                        to_year: frm.doc.to_year,
                        sub_activity_link: row.sub_activity_link,

                    },
                callback: function(r) {
                    if (r.message && r.message.irt_rating > 0) {
                        frappe.model.set_value(cdt, cdn, "irt_rating", r.message.irt_rating);        
                        frappe.model.set_value(cdt, cdn, "weighted_score", r.message.weighted_score);
                        frappe.model.set_value(cdt, cdn, "category", r.message.category);
                    }else{
                        frappe.model.set_value(cdt, cdn, "irt_rating", "0"); 
                        frappe.model.set_value(cdt, cdn, "weighted_score", 0);
                        frappe.model.set_value(cdt, cdn, "category", "");                                               
                    }
                    if (row.irt_rating > 0){
                        irt_rating(frm, cdt, cdn)
                        // frappe.trigger("irt_rating")
                    }
                    frm.refresh_field("irt_rating");
                    frm.refresh_field("weighted_score");
                    frm.refresh_field("category");
                }
            })
		// } 
	},
});
function irt_rating(frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    if (row.irt_rating) {
        frappe.call({
            method:"erpnext.budget.doctype.annual_performance_assessment.annual_performance_assessment.get_category_for_irt_rating",
            args: {
                    irt_rating: row.irt_rating,
                    unit: row.unit
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "category", r.message);
                    }else{
                        frappe.model.set_value(cdt, cdn, "category", "");   
                    }
                    frm.refresh_field("category");
                }
        })
    }
}