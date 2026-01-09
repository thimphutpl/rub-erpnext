frappe.ui.form.on("Club Action Plan", {
	refresh(frm) {
        // Set query for club_name in main form
        frm.set_query("club_name", function() {
			return {
				"filters": {
					"company": frm.doc.company
				}
			};
		});

        // Set query for activity field in child table
        
	}
});

