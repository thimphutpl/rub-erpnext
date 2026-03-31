// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Planning Activities", {
	refresh(frm) {
        toggle_child_fields(frm);
        if(frm.doc.is_capital){
            frm.set_value("is_current", 0)
        }
        if(frm.doc.is_current){
            frm.set_value("is_capital", 0)
            frm.set_value("funding_source", "")
        }
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
    }
});

function toggle_child_fields(frm) {
    let grid = frm.fields_dict.items.grid;

    if (frm.doc.unit === "Status of Work") {
        grid.update_docfield_property("unit", "hidden", 0);
        grid.update_docfield_property("raw_rating", "hidden", 0);
        grid.update_docfield_property("max", "hidden", 1);
        grid.update_docfield_property("min", "hidden", 1);
    } 
    else if (["Number", "Percent"].includes(frm.doc.unit)) {
        grid.update_docfield_property("unit", "hidden", 1);
        grid.update_docfield_property("raw_rating", "hidden", 1);
        grid.update_docfield_property("max", "hidden", 0);
        grid.update_docfield_property("min", "hidden", 0);
    } 
    else {
        // default: show all
        grid.update_docfield_property("unit", "hidden", 0);
        grid.update_docfield_property("raw_rating", "hidden", 0);
        grid.update_docfield_property("max", "hidden", 0);
        grid.update_docfield_property("min", "hidden", 0);
    }

    frm.refresh_field("items");
}