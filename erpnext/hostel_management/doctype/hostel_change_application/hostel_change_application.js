// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Change Application", {
	refresh(frm) {    
        frm.set_query("requested_room", function() {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        });
	},
    applied_by: function(frm) {
        if (frm.doc.applied_by) {
            fetch_student_details(frm);
        }
    },
    student_code:function(frm) {
        if (frm.doc.student_code) {
            fetch_request_student_details(frm)
        }
    },
    current_room: function(frm) {
        validate_room_selection(frm);
    },
    qrc: function(frm) {
        if (frm.doc.qrc) {
            frm.set_value("student_code", 0);
            frm.set_value("room");
            frm.set_value("type")
        } else {
            frm.set_value("student_code", 1);
            frm.set_value("room", 1);
            frm.set_value("type")
        }
    },
    room: function(frm) {
        if (frm.doc.current_room && frm.doc.room && frm.doc.current_room === frm.doc.room) {
            frappe.msgprint(__('Current room and new room cannot be the same'));
            frm.set_value('room', ''); 
        }
    }
    
});


function fetch_student_details(frm) {
    frappe.call({
        method: 'erpnext.hostel_management.doctype.hostel_change_application.hostel_change_application.get_hostel_change_details',
        args: {
            student_code: frm.doc.applied_by
        },
        callback: function(response) {
            if (response.message && Object.keys(response.message).length) {
                const data = response.message;

                frm.set_value('first_name', data.first_name || '');
                frm.set_value('last_name', data.last_name || '');

                if (data.current_room) {
                    frm.set_value('current_room', data.current_room);
                } else {
                    frappe.msgprint(__('No current room found for this student'));
                }
            } else {
                frappe.msgprint(__('No current room is found for this student code'));
            }
        },
    });
}


function fetch_request_student_details(frm) {
    frappe.call({
        method: 'erpnext.hostel_management.doctype.hostel_change_application.hostel_change_application.get_change_request_room',
        args: {
            student_code: frm.doc.student_code
        },
        callback: function(response) {
            if (response.message) {
                const data = response.message;
                frm.set_value('room', data.room || '');
                frm.set_value('type', data.type || '');
                frm.refresh_field('room');
                frm.refresh_field('type');
            } else {
                frappe.msgprint(__('No room found for this student'));
            }
        },
    });
}
