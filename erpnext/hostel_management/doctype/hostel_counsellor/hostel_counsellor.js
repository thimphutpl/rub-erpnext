// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Counsellor", {
    refresh(frm) {
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__('Get Hostel Rooms'), function() {
                const hostel_types = frm.doc.hostel_type.map(d => d.hostel_type).join(",");

                frappe.call({
                    method: "erpnext.hostel_management.doctype.hostel_counsellor.hostel_counsellor.get_hostel_rooms_with_students",
                    args: {
                        company: frm.doc.company,
                        hostel_types: hostel_types
                    },
                    callback: function(r) {
                        frm.clear_table("table_lbtp");

                        if (r.message && r.message.length) {
                            r.message.forEach(function(room) {
                                if (room.students && room.students.length) {
                                    room.students.forEach(function(s) {
                                        let row = frm.add_child("table_lbtp");
                                        row.room_number = room.room_number;
                                        row.hostel_capacity = room.hostel_capacity;
                                        row.hostel_type = room.hostel_type;
                                        row.student_code = s.student_code;
                                        row.first_name = s.first_name;
                                        row.last_name = s.last_name;
                                    });
                                } else {
                                    let row = frm.add_child("table_lbtp");
                                    row.room_number = room.room_number;
                                    row.hostel_capacity = room.hostel_capacity;
                                    row.hostel_type = room.hostel_type;
                                }
                            });

                            frm.refresh_field("table_lbtp");
                            frappe.msgprint(__('Hostel rooms with student details have been fetched successfully.'));
                        } else {
                            frappe.msgprint(__('No rooms found for the selected hostel types.'));
                        }
                    }
                });
            });
        }
        frm.set_query("hostel_type", function() {
            return {
                filters: { company: frm.doc.company }
            };
        });
    }
});
