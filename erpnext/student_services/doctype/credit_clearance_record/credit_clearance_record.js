// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Credit Clearance Record", {
	refresh(frm) {
        frm.set_query("credit_type",function(){
             return {

                "filters": {
					"company": frm.doc.company
				
				}

            };

        });

        frm.set_query("student_code","student_details",function(){
            return {

                "filters": {
					"company": frm.doc.company
				
				}

            };

        })

	},

    get_students:function(frm){

        if(frm.doc.college && frm.doc.credit_type) {
			//load_accounts(frm.doc.company)
			return frappe.call({
                args: {
                    college: frm.doc.college,
                    credit_type:frm.doc.credit_type,

                },
				method: "get_students",
				doc: frm.doc,
				callback: function(r, rt) {
					frm.refresh_field("student_details");
					frm.refresh_fields();
				},
				freeze: true,
				freeze_message: "Loading Students Details..... Please Wait"
			});
		}
		else {
			msgprint("Select Company  and Credit Type")
		}

    
    }
});
