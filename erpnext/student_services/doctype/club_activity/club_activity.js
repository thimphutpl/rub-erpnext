// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Club Activity", {
	refresh(frm) {
        frm.set_query("club_name", function() {
			return {
				"filters": {
					"company": frm.doc.company
				
				}
			};
		});

        frm.set_query("activity_name", function() {
			return {
                query: "erpnext.controllers.queries.club_action_plan_query",
				filters: {
					"club_name": frm.doc.club_name,
                    "company": frm.doc.company,
                    "club_action_plan": frm.doc.club_action_plan
				}
			};
		});
        frm.set_query("club_name", function() {
			return {
				"filters": {
					"club_name": frm.doc.club_name,
				}
			};
		});

        // frm.set_query("activity_name", function() {
        //     return {
        //         filters: {
        //             "parent": frm.doc.club_action_plan
        //         },
        //         fields: ["name", "activity_name"]
        //     };
        //     });

            // cur_frm.fields_dict['activity_name'].df.onchange = function() {
            //         if (frm.doc.activity_name) {
            //             frappe.db.get_value('Club Action Plan Details', frm.doc.activity_name, 'activity_name')
            //             .then(r => {
            //                 if (r.message) {
            //                     // Display activity_type in a custom field or alert
            //                     frm.set_value('activity', r.message.activity_name);
            //                 }
            //             });
            //         }
            //     };
       

	},
    company: function(frm){
        frm.set_query("activity_name", function() {
			return {
                query: "erpnext.controllers.queries.club_action_plan_query",
				filters: {
					"club_name": frm.doc.club_name,
                    "company": frm.doc.company,
                    "club_action_plan": frm.doc.club_action_plan
				}
			};
		});
    },
    activity_name: function(frm){
        frappe.flag
        if(frm.doc.activity_name) {
            frappe.call({
                method: 'get_activity_name',
                doc: frm.doc,
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('activity', r.message);
                        frm.refresh_field('activity');
                    }
                }
            });
        }
    },
    club_action_plan: function(frm){
        frm.set_query("activity_name", function() {
			return {
                query: "erpnext.controllers.queries.club_action_plan_query",
				filters: {
					"club_name": frm.doc.club_name,
                    "company": frm.doc.company,
                    "club_action_plan": frm.doc.club_action_plan
				}
			};
		});
    },
	club_name: function(frm) {
    frm.set_query("activity_name", function() {
        return {
            "query": "erpnext.controllers.queries.club_action_plan_query",
            "filters": {
                "club_name": frm.doc.club_name,
                "company": frm.doc.company,
                "club_action_plan": frm.doc.club_action_plan
            }
        };
    });
    if (!frm.doc.club_name) return;
    
    frm.call({
        method: "get_coordinators",
        args: {
            club_name: frm.doc.club_name
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
            
                frm.clear_table("club_coordinator_details");
                
                
                r.message.forEach(function(coordinator) {
                    var child = frm.add_child("club_coordinator_details");
                    child.student_code = coordinator.student_code;
					child.first_name = coordinator.first_name;
					child.last_name = coordinator.last_name;
                    child.parentfield = "club_coordinator_details";
                    child.parenttype = frm.doctype;
                });
                
                frm.refresh_field("club_coordinator_details");
                
                
                frappe.show_alert({
                    message: __("{0} coordinator(s) found and added", [r.message.length]),
                    indicator: 'green'
                });
            } else {
                
                frm.clear_table("club_coordinator_details");
                frm.refresh_field("club_coordinator_details");
                frappe.show_alert({
                    message: __("No coordinators found for this club"),
                    indicator: 'orange'
                });
            }
        }
    });
},

    get_attendance:function(frm){

        if(frm.doc.club_name) {
			//load_accounts(frm.doc.company)
			return frappe.call({
                args: {
                    club_name: frm.doc.club_name
                },
				method: "get_attendance_club_activites",
				doc: frm.doc,
				callback: function(r, rt) {
					frm.refresh_field("club_attendance_details");
					frm.refresh_fields();
				},
				freeze: true,
				freeze_message: "Loading Employee Details..... Please Wait"
			});
		}
		else {
			msgprint("Select Fiscal Year First")
		}

    
    }
});
