// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Approved Budget", {
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
});

frappe.ui.form.on("APA Detail Extra", {
	form_render: function(frm, cdt, cdn) {
        let grid_row = frm.fields_dict.apa_extra_details.grid.grid_rows_by_docname[cdn];
        if (grid_row) {
            grid_row.toggle_display("proposed_budget", false);
        }
    }
});
