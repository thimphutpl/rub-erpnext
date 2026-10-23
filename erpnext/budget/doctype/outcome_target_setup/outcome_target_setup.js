// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Outcome Target Setup", {
	refresh(frm) {
        // frm.set_df_property('items', 'cannot_add_rows', true);
        // frm.set_df_property('items', 'cannot_delete_rows', true);
        // refresh_field('items');
        toggle_child_fields(frm);
	},
    setup(frm){
        frm.set_query("college", function () {
            return {
                filters: {
                    is_group: 0,
                    is_overseeing_company: 0,
                },
            };
        });
    },
    unit: function(frm){
        toggle_child_fields(frm);
    },
    is_not_range: function(frm){
        toggle_child_fields(frm, false, true);
    }
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

// function toggle_child_fields(frm) {
//     let grid = frm.fields_dict.items.grid;

//     if (frm.doc.unit === "Status of Work") {
//         (frm.doc.items || []).forEach(row => {
//             row.max = null;
//             row.min = null;
//         });
//         grid.update_docfield_property("unit", "hidden", 0);
//         grid.update_docfield_property("raw_rating", "hidden", 0);
//         grid.update_docfield_property("max", "hidden", 1);
//         grid.update_docfield_property("min", "hidden", 1);
//     } 
//     else if (["Number", "Percent"].includes(frm.doc.unit)) {
//         (frm.doc.items || []).forEach(row => {
//             row.raw_rating = null;
//         });
//         grid.update_docfield_property("unit", "hidden", 1);
//         grid.update_docfield_property("raw_rating", "hidden", 1);
//         grid.update_docfield_property("max", "hidden", 0);
//         grid.update_docfield_property("min", "hidden", 0);
//     } 
//     else {
//         // default: show all
//         grid.update_docfield_property("unit", "hidden", 1);
//         grid.update_docfield_property("raw_rating", "hidden", 1);
//         grid.update_docfield_property("max", "hidden", 1);
//         grid.update_docfield_property("min", "hidden", 1);
//     }

//     frm.refresh_field("items");
// }