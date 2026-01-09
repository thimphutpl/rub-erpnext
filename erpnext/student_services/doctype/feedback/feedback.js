// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Feedback", {
	refresh(frm) {
        

        $(".timeline-items").hide();
        $(".timeline-item activity-title").hide();
        
        $(".comment-box").hide();
        $(".modified-by").hide();
        $(".created-by").hide();
	},
});
