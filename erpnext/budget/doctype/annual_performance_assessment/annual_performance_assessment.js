// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Annual Performance Assessment", {
	// refresh(frm) {
        
	// },
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
        frm.trigger("fetch_output_and_outcome");
    },
    to_year: function(frm) {
        frm.trigger("fetch_output_and_outcome");
    },
    college: function(frm) {
        frm.trigger("fetch_output_and_outcome");
    },
    fetch_output_and_outcome: function(frm){
        if(frm.doc.from_year && frm.doc.to_year && frm.doc.college){
            frappe.call({
                method:"erpnext.budget.doctype.annual_performance_assessment.annual_performance_assessment.fetch_output_and_outcome",
                args: {
                        from_year: frm.doc.from_year,
                        to_year: frm.doc.to_year,
                        college: frm.doc.college
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
                                child.activities_no = row.activities_no
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
                            });
        
                            frm.refresh_field("output_extra_items");
                        }
                        if (r.message.outcome) {
                            console.log(r.message.outcome)
                            frm.clear_table("outcome_items");
                            
                            r.message.outcome.forEach(function(row) {
                                let child = frm.add_child("outcome_items");
                                child.outcome = row.outcome
                                child.unit= row.unit
                                child.weightage = row.weightage
                                child.target = row.target
                            });
        
                            frm.refresh_field("outcome_items");
                        }
                    }
            })
        }
    }
});

frappe.ui.form.on("APA Outcome Item", {
    raw_rating: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.raw_rating) {
			frappe.call({
                method:"erpnext.budget.doctype.annual_performance_assessment.annual_performance_assessment.calculate_outcome_irt_rating",
                args: {
                        raw_rating: row.raw_rating,
                        outcome: row.outcome,
                        unit: row.unit,
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.model.set_value(cdt, cdn, "irt_rating", r.message);        
                            frm.refresh_field("irt_rating");
                        }
                        if (row.irt_rating){
                            frappe.trigger("irt_rating")
                        }
                    }
            })
		} else {
			// frm.script_manager.copy_from_first_row("items", row, ["delivery_date"]);
		}
	},
    irt_rating: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
        if (row.irt_rating) {
			frappe.call({
                method:"erpnext.budget.doctype.annual_performance_assessment.annual_performance_assessment.get_category_for_irt_rating",
                args: {
                        irt_rating: row.irt_rating,
                        // outcome: row.outcome
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.model.set_value(cdt, cdn, "category", r.message);
                            frm.refresh_field("category");
                        }
                    }
            })
		}
    }
});

frappe.ui.form.on("APA Output Item", {
    raw_rating: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.raw_rating) {
			frappe.call({
                method:"erpnext.budget.doctype.annual_performance_assessment.annual_performance_assessment.calculate_output_irt_rating",
                args: {
                        raw_rating: row.raw_rating,
                        activity_link: row.activity_link,
                        unit: row.unit,
                        weightage: row.weightage,
                        sub_activity_no: row.sub_activity_no,
                    },
                    callback: function(r) {
                        if (r.message) {
                            if (r.message) {
                                frappe.model.set_value(cdt, cdn, "irt_rating", r.message.irt_rating);        
                                frappe.model.set_value(cdt, cdn, "weighted_score", r.message.weighted_score);                                       
                                frm.refresh_field("irt_rating");
                                frm.refresh_field("weighted_score");
                            }
                            if (row.irt_rating){
                                frappe.trigger("irt_rating")
                            }
                        }
                        if (row.irt_rating){
                            frappe.trigger("irt_rating")
                        }
                    }
            })
		} else {
			// frm.script_manager.copy_from_first_row("items", row, ["delivery_date"]);
		}
	},
    irt_rating: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
        if (row.irt_rating) {
			frappe.call({
                method:"erpnext.budget.doctype.annual_performance_assessment.annual_performance_assessment.get_category_for_irt_rating",
                args: {
                        irt_rating: row.irt_rating,
                        // outcome: row.outcome
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.model.set_value(cdt, cdn, "category", r.message);
                            frm.refresh_field("category");
                        }
                    }
            })
		}
    }
});