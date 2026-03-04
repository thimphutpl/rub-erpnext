// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Club Membership List", {
	refresh(frm) {
        frm.set_query('club_name',function(){
            return {
				"filters": {
					"company": frm.doc.college
				
				}

        };


    });

	},
    "get_member":function(frm){
        return frm.call({
             method:"get_member",
             doc:frm.doc,
             //args:{"college":frm.doc.college,"club_name":frm.doc.club_name},

        });
    }


});

