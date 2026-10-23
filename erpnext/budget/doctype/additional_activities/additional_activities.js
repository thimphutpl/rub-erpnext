// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Additional Activities", {
    refresh(frm) {
        toggle_child_fields(frm);
        if(frm.doc.is_capital){
            frm.set_value("is_current", 0)
        }
        if(frm.doc.is_current){
            frm.set_value("is_capital", 0)
            frm.set_value("funding_source", "")
        }
        frm.set_query("department", function () {
            return {
                filters: {
                    company: "Office of Vice Chancellor",
                    include_in_apa: 1
                },
            };
        });
        set_activity_filter(frm);

	},
    is_current: function(frm){
        if(frm.doc.is_current){
            frm.set_value("is_capital", 0)
            frm.set_value("funding_source", "")
        }
    },
    is_capital: function(frm){
        if(frm.doc.is_capital){
            frm.set_value("is_current", 0)
        }
    },
    unit: function(frm){
        toggle_child_fields(frm);
    },
    include_in_apa: function(frm) {
        frm.set_value("unit", null)
        frm.clear_table("items");
        frm.refresh_field("items");
    },
    is_not_range: function(frm){
        toggle_child_fields(frm, false, true);
    },
    college: function(frm) {
        set_activity_filter(frm);
    },
    from_year: function(frm) {
        set_activity_filter(frm);
    },
    to_year: function(frm) {
        set_activity_filter(frm);
    },
    department: function(frm) {
        set_activity_filter(frm);
    },
});

function toggle_child_fields(frm, clear_table = false, clear_fields = false) {
    let grid = frm.fields_dict.items.grid;

    if (clear_table) {
        frm.clear_table("items");
        frm.set_value("is_not_range", 0);
    }

    if (clear_fields) {
        (frm.doc.items || []).forEach(row => {
            frappe.model.set_value(row.doctype, row.name, "min", null);
            frappe.model.set_value(row.doctype, row.name, "max", null);
            frappe.model.set_value(row.doctype, row.name, "unit", null);
            frappe.model.set_value(row.doctype, row.name, "raw_rating", null);
        });
    }

    if (frm.doc.unit === "Status of Work") {
        (frm.doc.items || []).forEach(row => {
            row.max = null;
            row.min = null;
        });
        grid.update_docfield_property("unit", "hidden", 0);
        grid.update_docfield_property("raw_rating", "hidden", 0);
        grid.update_docfield_property("max", "hidden", 1);
        grid.update_docfield_property("min", "hidden", 1);
    } 
    else if (["Number", "Percent", "Survey"].includes(frm.doc.unit)) {
        // (frm.doc.items || []).forEach(row => {
        //     row.raw_rating = null;
        // });
        if(frm.doc.is_not_range == 1){
            grid.update_docfield_property("unit", "hidden", 0);
            grid.update_docfield_property("raw_rating", "hidden", 0);
            grid.update_docfield_property("max", "hidden", 1);
            grid.update_docfield_property("min", "hidden", 1);
        }else{
            grid.update_docfield_property("unit", "hidden", 1);
            grid.update_docfield_property("raw_rating", "hidden", 1);
            grid.update_docfield_property("max", "hidden", 0);
            grid.update_docfield_property("min", "hidden", 0);
        }
    } 
    else {
        // default: show all
        grid.update_docfield_property("unit", "hidden", 1);
        grid.update_docfield_property("raw_rating", "hidden", 1);
        grid.update_docfield_property("max", "hidden", 1);
        grid.update_docfield_property("min", "hidden", 1);
    }

    frm.refresh_field("items");
}

function set_activity_filter(frm) {
    frm.set_query("activity", function() {
        return {
            query: "erpnext.budget.doctype.apa_sub_activities.apa_sub_activities.get_planning_activities",
            filters: {
                college: frm.doc.college,
                from_year: frm.doc.from_year,
                to_year: frm.doc.to_year,
                department: frm.doc.department,
            }
        };
    });
}
