// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Councillor", {
    refresh(frm) {
        frm.fields_dict["hostel_councilor"].grid.get_field("student_id").get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        };
        frm.set_query("company", function(){
			return {
				filters: {
					"is_group": 0,
				}
			}
		});
        frm.set_query("hostel_room", function() {
            if (!frm.doc.company) {
                return { filters: [["name", "=", ""]] };
            }
        
            let hostel_types = [];
        
            if (frm.doc.hostel_type && frm.doc.hostel_type.length) {
                frm.doc.hostel_type.forEach(row => {
                    if (row.hostel_type) {
                        hostel_types.push(row.hostel_type);
                    }
                });
            }
        
            let filters = {
                company: frm.doc.company
            };
        
            if (hostel_types.length) {
                filters.hostel_type = ["in", hostel_types];
            }
        
            return { filters: filters };
        });

        frm.set_query("hostel_type", function() {
            return {
                filters: { company: frm.doc.company }
            };
        });
    },
    
    get_hostel_rooms: function(frm) {

        // Hostel Types
        const hostel_types = frm.doc.hostel_type.map(d => d.hostel_type).join(",");
    
        // Hostel Rooms (NEW)
        const hostel_rooms = frm.doc.hostel_room.map(d => d.hostel_room).join(",");
    
        if (!hostel_types) {
            frappe.msgprint({
                title: __('No Hostel Types'),
                message: __('Please select at least one Hostel Type'),
                indicator: 'orange'
            });
            return;
        }
    
        frappe.show_alert({
            message: __('Fetching selected hostel rooms...'),
            indicator: 'blue'
        });
    
        frappe.call({
            method: "erpnext.hostel_management.doctype.hostel_councillor.hostel_councillor.get_hostel_rooms_with_students",
            args: {
                company: frm.doc.company,
                hostel_types: hostel_types,
                hostel_rooms: hostel_rooms || null
            },
            callback: function(r) {
                frm.clear_table("table_lbtp");
    
                if (r.message && r.message.length) {
                    let total_students = 0;
    
                    r.message.forEach(room => {
                        if (room.students) {
                            total_students += room.students.length;
    
                            room.students.forEach(s => {
                                let row = frm.add_child("table_lbtp");
                                row.room_number = room.room_number;
                                row.hostel_capacity = room.hostel_capacity;
                                row.hostel_type = room.hostel_type;
                                row.student_code = s.student_code;
                                row.first_name = s.first_name;
                                row.last_name = s.last_name;
                            });
                        }
                    });
    
                    frm.refresh_field("table_lbtp");
    
                    frappe.msgprint({
                        title: __('Success'),
                        message: __(`Found {0} rooms with {1} students`).format(
                            r.message.length,
                            total_students
                        ),
                        indicator: 'green'
                    });
                } else {
                    frappe.msgprint({
                        title: __('No Data Found'),
                        message: __('No rooms with students found'),
                        indicator: 'orange'
                    });
                }
            }
        });
    }
});
