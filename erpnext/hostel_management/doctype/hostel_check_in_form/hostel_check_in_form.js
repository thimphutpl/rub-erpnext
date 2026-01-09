// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Check-In Form", {
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
			return {
				filters: {
					company: frm.doc.company
				}
			}
		}); 
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
});
