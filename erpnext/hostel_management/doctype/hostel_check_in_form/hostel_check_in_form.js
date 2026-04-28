// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Check-In Form", {
    onload(frm){
        if (!frm.doc.posting_date) {
			frm.set_value('posting_date', frappe.datetime.now_date());
			// frm.set_value("posting_date", get_today());
		}
    },
	refresh(frm) {
        if (!frm.doc.hostel_check_out_form && frm.doc.docstatus == 1)  {
			frm.add_custom_button(__("Hostel Check-Out Form"), function () {
				frm.trigger("create_hostel_check_out_form");
				},
				__("Create")
			);
		}
		frm.set_query("company", function(){
			return {
				filters: {
					"is_group": 0,
				}
			}
		}); 
        frm.set_query("hostel_room", function(){
            if (!frm.doc.company) {
                return {
                    filters: [
                        ["name", "=", ""]  // Return empty result
                    ]
                };
            }
			return {
				filters: {
					company: frm.doc.company
				}
			}
		}); 

        // Set query for the 'student' field inside 'check_in_asset_items' child table
        frm.set_query('student', 'assets', function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            
            if (!doc.hostel_room) {
                frappe.msgprint(__('Please select a Hostel Room first'));
                return { filters: [] };
            }
            
            // Fetch the selected Hostel Room document to get its student list
            return {
                query: "erpnext.hostel_management.doctype.hostel_check_in_form.hostel_check_in_form.get_filtered_students",
                filters: {
                    'hostel_room': doc.hostel_room
                }
            };
        });
        
        // Add date validation on form load
        validate_posting_date(frm);
	},
    hostel_room: function(frm) {
        if (!frm.doc.company) {
            frappe.msgprint(__('Please select a College first'));
            frm.set_value('hostel_room', ''); 
            // frappe.validated = false; 
            return false;
        }
    },
    
    hostel_type: function(frm) {
        if (!frm.doc.company) {
            frm.set_value('hostel_type', ''); 
            frappe.validated = false;
            return false;
        }
    },

    get_students: function(frm) {
        if (!frm.doc.hostel_room) {
            frappe.msgprint(__('Please select a Hostel Room'));
            return;
        }

        frappe.call({
            method: 'erpnext.hostel_management.doctype.hostel_check_in_form.hostel_check_in_form.get_students_from_room',
            args: {
                hostel_room: frm.doc.hostel_room
            },
            callback: function(r) {
                if (r.message) {
                    // Clear existing rows
                    frm.clear_table('students');

                    r.message.forEach(row => {
                        let child = frm.add_child('students');
                        child.student_code = row.student_code;
                        child.year = row.year;
                    });

                    frm.refresh_field('students');
                }
            }
        });
    },
    get_assets: function(frm) {
        if (!frm.doc.hostel_room) {
            frappe.msgprint(__('Please select a Hostel Room'));
            return;
        }

        frappe.call({
            method: 'erpnext.hostel_management.doctype.hostel_check_in_form.hostel_check_in_form.get_assets_from_room',
            args: {
                hostel_room: frm.doc.hostel_room
            },
            callback: function(r) {
                if (r.message) {
                    // Clear existing rows
                    frm.clear_table('assets');

                    r.message.forEach(row => {
                        let child = frm.add_child('assets');
                        child.asset_code = row.asset_code;
                        child.asset_name = row.asset_name;
                    });

                    frm.refresh_field('assets');
                }
            }
        });
    },
    create_hostel_check_out_form: function (frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.hostel_management.doctype.hostel_check_in_form.hostel_check_in_form.make_checkout_form",
			frm: cur_frm
		})
	},
    posting_date: function(frm) {
        validate_posting_date(frm);
    },
    
    fiscal_year: function(frm) {
        // Clear posting_date if it becomes invalid when fiscal year changes
        if (frm.doc.posting_date && frm.doc.fiscal_year) {
            validate_posting_date(frm, function(is_valid) {
                if (!is_valid) {
                    frm.set_value('posting_date', '');
                    frappe.msgprint(__('Posting Date cleared because it is not within the selected Fiscal Year'));
                }
            });
        }
    },    
});

function validate_posting_date(frm, callback) {
    if (!frm.doc.posting_date || !frm.doc.fiscal_year) {
        if (callback) callback(true);
        return;
    }
    
    frappe.call({
        method: "erpnext.hostel_management.doctype.hostel_check_in_form.hostel_check_in_form.validate_posting_date",
        args: {
            "posting_date": frm.doc.posting_date,
            "fiscal_year": frm.doc.fiscal_year
        },
        callback: function(r) {
            if (r.message && !r.message.is_valid) {
                frappe.msgprint({
                    title: __('Invalid Date'),
                    message: __(`Posting Date ${frappe.datetime.str_to_user(frm.doc.posting_date)} is not within Fiscal Year ${frm.doc.fiscal_year} (${r.message.year_start_date} to ${r.message.year_end_date})`),
                    indicator: 'red'
                });
                
                // Clear the invalid date
                frm.set_value('posting_date', '');
                
                if (callback) callback(false);
            } else {
                if (callback) callback(true);
            }
        }
    });
}
