// Copyright (c) 2025, Frappe Technologies Pvt. Ltd.
// For license information, please see license.txt

frappe.ui.form.on("Hostel Attendance", {
    refresh(frm) {
        frm.set_query("hostel_block", function(doc) {
            return { filters: { company: doc.company } };
        });

        if (!frm.doc.__islocal) {
            frm.add_custom_button(__('Get Hostel Attendance'), function() {
                frappe.call({
                    method: "erpnext.hostel_management.doctype.hostel_attendance.hostel_attendance.get_hostel_attendance",
                    args: {
                        company: frm.doc.company,
                        hostel_block: frm.doc.hostel_block
                    },
                    callback: function(r) {
                        frm.clear_table("table_tulk");

                        if (r.message && r.message.length) {
                            r.message.forEach(function(item) {
                                let row = frm.add_child("table_tulk");
                                row.room_number = item.room_number;
                                row.student_code = item.student_code;
                                row.student_name = item.student_name;  
                            });
                            frm.refresh_field("table_tulk");
                            frappe.msgprint(__('Hostel attendance data fetched successfully.'));
                        } else {
                            frappe.msgprint(__('No rooms found for this hostel block.'));
                        }
                    }
                });
            });
        }
    },
});
