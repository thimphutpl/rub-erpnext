// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Check-Out Form", {
    onload(frm){
        if (!frm.doc.posting_date) {
			frm.set_value('posting_date', frappe.datetime.now_date());
			// frm.set_value("posting_date", get_today());
		}
    },
	refresh(frm) {
        frm.set_query("student", function(){
			return {
				filters: {
					"company": frm.doc.college,
				}
			}
		});
        // Add date validation on form load
        validate_posting_date(frm);
	},
    student: function(frm) {
        if (!frm.doc.student) {
            frm.clear_table('table_snes');
            frm.refresh_field('table_snes');
            return;
        }
        
        if (!frm.doc.fiscal_year) {
            frappe.msgprint(__('Please select a Fiscal Year first'));
            frm.set_value('student', '');
            return;
        }
        
        // Fetch assets from Hostel Check-In Form
        fetch_student_assets(frm);
    },
    
    // fiscal_year: function(frm) {
    //     if (frm.doc.student) {
    //         // Clear existing assets and fetch new ones
    //         frm.clear_table('table_snes');
    //         fetch_student_assets(frm);
    //     }
    // },
    posting_date: function(frm) {
        validate_posting_date(frm);
    },
    
    fiscal_year: function(frm) {
        if (frm.doc.student) {
            // Clear existing assets and fetch new ones
            frm.clear_table('table_snes');
            fetch_student_assets(frm);
        }

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

function fetch_student_assets(frm) {
    frappe.call({
        method: "erpnext.hostel_management.doctype.hostel_check_out_form.hostel_check_out_form.get_student_assets_from_check_in",
        args: {
            "student": frm.doc.student,
            "fiscal_year": frm.doc.fiscal_year
        },
        callback: function(r) {
            if (r.message) {
                if (r.message.length === 0) {
                    frappe.msgprint({
                        title: __('No Assets Found'),
                        message: __('No checked-in assets found for this student in the selected fiscal year.'),
                        indicator: 'orange'
                    });
                } else {
                    // Clear existing rows
                    frm.clear_table('table_snes');
                    
                    // Add assets to child table
                    r.message.forEach(asset => {
                        let row = frm.add_child('table_snes');
                        row.student = asset.student;
                        row.asset_code = asset.asset_code;
                        row.asset_name = asset.asset_name;
                        row.item_code = asset.item_code;
                        row.item_name = asset.item_name;
                        row.check_in_date = asset.check_in_date;
                        row.check_in_form = asset.check_in_form;
                        row.remarks = asset.remarks;
                        row.unique_serial_no = asset.unique_serial_no;
                        // Add any other fields you have
                    });
                    
                    frm.refresh_field('table_snes');
                    
                    frappe.show_alert({
                        message: __(`Loaded ${r.message.length} assets for checkout`),
                        indicator: 'green'
                    }, 3);
                }
            }
        },
        error: function(err) {
            frappe.msgprint({
                title: __('Error'),
                message: __('Failed to fetch assets. Please try again.'),
                indicator: 'red'
            });
        }
    });
}

function validate_posting_date(frm, callback) {
    if (!frm.doc.posting_date || !frm.doc.fiscal_year) {
        if (callback) callback(true);
        return;
    }
    
    frappe.call({
        method: "erpnext.hostel_management.doctype.hostel_check_out_form.hostel_check_out_form.validate_posting_date",
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
