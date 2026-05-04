// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Allocation Bulk Upload", {
    onload: function(frm) {
        if (!frm.doc.posting_date) {
			frm.set_value('posting_date', frappe.datetime.now_date());
			// frm.set_value("posting_date", get_today());
		}
        frm.set_query("company", function(){
			return {
				filters: {
					"is_group": 0,
				}
			}
		}); 
        frm.set_query("hostel_type", function() {
            if (!frm.doc.company) {
                return {
                    filters: [
                        ["company", "=", ""]  // Return empty result
                    ]
                };
            }
            return {
                filters: { company: frm.doc.company }
            };
        });  
        frm.fields_dict["table_caon"].grid.get_field("hostel_room").get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        };


        frm.fields_dict["table_caon"].grid.get_field("student_code").get_query = function(doc, cdt, cdn) {
            let opposite_gender = null;
            return {
                filters: {
                    company: frm.doc.company,
                    year: frm.doc.year

                }
            };
        };
    },   
    
    get_student: function(frm) {
        if (!frm.doc.year) {
            frappe.msgprint("Please select Year");
            return;
        }
        if (!frm.doc.gender) {
            frappe.msgprint("Please select Gender");
            return;
        }
        if (!frm.doc.company) {
            frappe.msgprint("Please select College");
            return;
        }

        frappe.call({
            method: "erpnext.hostel_management.doctype.hostel_allocation_bulk_upload.hostel_allocation_bulk_upload.get_students",
            args: {
                year: frm.doc.year,
                gender: frm.doc.gender,
                company: frm.doc.company
            },
            callback: function(r) {
                if (r.message) {
                    frm.clear_table("table_caon");

                    r.message.forEach(student => {
                        let row = frm.add_child("table_caon");
                        row.student_code = student.name;
                        row.first_name = student.first_name;
                        row.middle_name = student.middle_name;
                        row.last_name = student.last_name;
                        row.gender = student.gender;
                        row.catering_type = student.catering_type;
                        row.scholarship_type = student.scholarship_type;
                        row.status = student.status;
                    });

                    frm.refresh_field("table_caon");
                }
            }
        });
    },

    hostel_allocation: function(frm) {

        if (!frm.doc.company || !frm.doc.year) {
            frappe.msgprint("Please select Company and Year");
            return;
        }
    
        if (!frm.doc.hostel_type || !frm.doc.hostel_type.length) {
            frappe.msgprint("Please select Hostel Type");
            return;
        }
    
        if (!frm.doc.table_caon || !frm.doc.table_caon.length) {
            frappe.msgprint("Please fetch students first");
            return;
        }
    
        // -------------------------
        // 1. Get Hostel Types
        // -------------------------
        let hostel_types = frm.doc.hostel_type.map(d => d.hostel_type);
    
        // -------------------------
        // 2. Get Students (only unassigned)
        // -------------------------
        let students = [];
    
        frm.doc.table_caon.forEach(row => {
            if (!row.hostel_room && row.student_code) {
                students.push({
                    student_code: row.student_code
                });
            }
        });
    
        if (!students.length) {
            frappe.msgprint("All students already allocated");
            return;
        }
    
        frappe.show_alert({
            message: "Auto allocating rooms...",
            indicator: "blue"
        });
    
        frappe.call({
            method: "erpnext.hostel_management.doctype.hostel_allocation_bulk_upload.hostel_allocation_bulk_upload.auto_allocate_rooms",
            args: {
                company: frm.doc.company,
                year: frm.doc.year,
                hostel_types: hostel_types.join(","),
                students: JSON.stringify(students)
            },
            callback: function(r) {
    
                if (!r.message || !r.message.length) {
                    frappe.msgprint("No rooms available for allocation");
                    return;
                }
    
                // -------------------------
                // 3. Apply Allocation
                // -------------------------
                let allocation_map = {};
    
                r.message.forEach(a => {
                    allocation_map[a.student_code] = a.hostel_room;
                });
    
                frm.doc.table_caon.forEach(row => {
                    if (!row.hostel_room && allocation_map[row.student_code]) {
                        row.hostel_room = allocation_map[row.student_code];
                    }
                });
    
                frm.refresh_field("table_caon");
    
                frappe.msgprint(`Allocated ${r.message.length} students successfully`);
            }
        });
    }
});







