// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("APA Mid Term Activity Change Request", {
    refresh: function(frm){
        if (!frm.doc.college || !frm.doc.from_year || !frm.doc.to_year || !frm.doc.add_drop) {
            frm.set_query("activity_name", function() {
                return {
                    filters: {
                        name: ["=", ""]  // Forces no results
                    }
                };
            })
        }
    },
    setup: function(frm){
        if (!frm.doc.college || !frm.doc.from_year || !frm.doc.to_year || !frm.doc.add_drop) {
            frm.set_query("activity_name", function() {
                return {
                    filters: {
                        name: ["=", ""]
                    }
                };
            })
        }
    },
    add_drop: function(frm){
        frm.set_value("activity_name", "")
        set_activity_query(frm);

    },
    from_year: function(frm){
        frm.set_value("activity_name", "")
        set_activity_query(frm);

    },
    to_year: function(frm){
        frm.set_value("activity_name", "");
        set_activity_query(frm);
    },
    college: function(frm){
        frm.set_value("activity_name", "");
        set_activity_query(frm);
    },
    activity_type: function(frm){
        frm.set_value("activity_name", "");
        set_activity_query(frm);
    },
});

function set_activity_query(frm) {
    if (frm.doc.from_year && frm.doc.to_year && frm.doc.college && frm.doc.add_drop) {
        frm.set_query("activity_name", function() {
            return {
                query: "erpnext.budget.doctype.apa_mid_term_activity_change_request.apa_mid_term_activity_change_request.get_filtered_activities",
                filters: {
                    'from_year': frm.doc.from_year, 
                    'to_year': frm.doc.to_year,
                    'college': frm.doc.college,
                    'add_drop': frm.doc.add_drop,
                    'activity_type': frm.doc.activity_type,
                }
            };
        });
    }
}