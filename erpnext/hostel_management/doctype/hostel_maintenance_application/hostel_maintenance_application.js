// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Maintenance Application", {
	onload (frm) {
		if (!frm.doc.posting_date) {
			frm.set_value('posting_date', frappe.datetime.now_date());
			// frm.set_value("posting_date", get_today());
		}
	},
	refresh(frm) {
		if (!frm.doc.hostel_maintenance_report && frm.doc.docstatus == 1 && frm.doc.workflow_state == "Approved")  {
			frm.add_custom_button(__("Hostel Maintenance Report"), function () {
				frm.trigger("create_maintenance_application");
				},
				__("Create")
			);
		}
		frm.set_query("college", function(){
			return {
				filters: {
					"is_group": 0,
				}
			}
		}); 
		frm.set_query("applied_by", function() {
            return {
                filters: {
                    company: frm.doc.college
                }
            };
        });
		frm.set_query("branch", function() {
            return {
                filters: {
                    company: frm.doc.college
                }
            };
        });
		frm.set_query("cost_center", function() {
            return {
                filters: {
                    company: frm.doc.college
                }
            };
        });
		frm.set_query("hostel_room", function() {
            return {
                filters: {
                    company: frm.doc.college
                }
            };
        });
        frm.set_query("hostel_room", function() {
            return {
                filters: {
                    company: frm.doc.college
                }
            };
        });
		frm.fields_dict["assets"].grid.get_field("asset").get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    hostel: frm.doc.hostel_room,

                }
            };
        };
	},
	create_maintenance_application: function (frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.hostel_management.doctype.hostel_maintenance_application.hostel_maintenance_application.make_maintenance_application",
			frm: cur_frm
		})
	},
	applied_by: function (frm) {
		fetch_checkin_form(frm);
		// frappe.throw("hh")
		if (frm.doc.applied_by) {
			frappe.call({
				method: "erpnext.hostel_management.doctype.hostel_maintenance_application.hostel_maintenance_application.get_hostel_room_by_student",
				args: {
					applied_by: frm.doc.applied_by
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value("hostel_room", r.message);
					} else {
						frappe.msgprint("No hostel room found for this student.");
						frm.set_value("hostel_room", "");
					}
				}
			});
		}
		
	},
	fiscal_year: function(frm) {
        fetch_checkin_form(frm);
        fetch_checkout_form(frm);
    },
	focal_type: function(frm) {
        if (frm.doc.focal_type && frm.doc.college) {
            set_maintenance_focal(frm);
        } else if (frm.doc.focal_type && !frm.doc.college) {
            frappe.msgprint({
                title: __('College Required'),
                message: __('Please select a College first'),
                indicator: 'orange'
            });
            frm.set_value('focal_type', '');
        }
    },
    
    college: function(frm) {
        if (frm.doc.college && frm.doc.focal_type) {
            set_maintenance_focal(frm);
        } else if (frm.doc.college && !frm.doc.focal_type) {
            // Optional: Show available focal types for this college
            get_available_focal_types(frm);
        }
    }
});

function fetch_checkin_form(frm) {
    console.log("Student:", frm.doc.applied_by);
    console.log("Fiscal Year:", frm.doc.fiscal_year);

    if (!frm.doc.applied_by || !frm.doc.fiscal_year) {
        console.log("Missing values");
        return;
    }

    frappe.call({
        method: "erpnext.hostel_management.doctype.hostel_maintenance_application.hostel_maintenance_application.get_hostel_checkin_form",
        args: {
            applied_by: frm.doc.applied_by,
            fiscal_year: frm.doc.fiscal_year
        },
        callback: function(r) {
            console.log("Response:", r);

            if (r.message) {
                frm.set_value("hostel_check_in_form", r.message);
            } else {
                console.log("No data found");
                frm.set_value("hostel_check_in_form", "");
            }
        }
    });
}

frappe.ui.form.on('Hostel Asset Maintenance', {
	asset: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.asset) {
			frappe.call({
				method: "erpnext.hostel_management.doctype.hostel_maintenance_application.hostel_maintenance_application.get_asset_rate",
				args: {
					asset: row.asset
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, 'rate', r.message);
					} else {
						frappe.model.set_value(cdt, cdn, 'rate', 0);
					}
				}
			});
		}
	}
});

function set_maintenance_focal(frm) {
    if (!frm.doc.focal_type || !frm.doc.college) {
        return;
    }
    
    // Map focal_type to field in Company
    const focal_field_map = {
        "Plumber": "plumber",
        "Electrician": "electrician",
        "Mason": "mason",
        "Carpenter": "carpenter"
    };
    
    const field_name = focal_field_map[frm.doc.focal_type];
    
    if (!field_name) {
        frappe.msgprint({
            title: __('Invalid Focal Type'),
            message: __('Please select a valid Focal Type'),
            indicator: 'red'
        });
        return;
    }
    
    frappe.call({
        method: "frappe.client.get_value",
        args: {
            doctype: "Company",
            filters: { name: frm.doc.college },
            fieldname: field_name
        },
        callback: function(r) {
            if (r.message && r.message[field_name]) {
                frm.set_value("maintenance_focal", r.message[field_name]);
                
                // Get employee details for display
                frappe.call({
                    method: "frappe.client.get_value",
                    args: {
                        doctype: "Employee",
                        filters: { name: r.message[field_name] },
                        fieldname: ["employee_name", "department", "cell_number"]
                    },
                    callback: function(emp_r) {
                        if (emp_r.message) {
                            let msg = __("Assigned {0}: {1}").format(
                                frm.doc.focal_type,
                                emp_r.message.employee_name
                            );
                            frappe.show_alert({
                                message: msg,
                                indicator: 'green'
                            }, 3);
                        }
                    }
                });
            } else {
                frappe.msgprint({
                    title: __('No Focal Person Found'),
                    message: __("No {0} assigned to {1}. Please assign one in Company master.").format(
                        frm.doc.focal_type,
                        frm.doc.college
                    ),
                    indicator: 'orange'
                });
                frm.set_value("maintenance_focal", "");
            }
        }
    });
}

function get_available_focal_types(frm) {
    frappe.call({
        method: "erpnext.hostel_management.doctype.hostel_maintenance_application.hostel_maintenance_application.get_company_focal_persons",
        args: {
            company: frm.doc.college
        },
        callback: function(r) {
            if (r.message) {
                let available = [];
                if (r.message.plumber) available.push("Plumber");
                if (r.message.electrician) available.push("Electrician");
                if (r.message.mason) available.push("Mason");
                if (r.message.carpenter) available.push("Carpenter");
                
                if (available.length > 0) {
                    frappe.msgprint({
                        title: __('Available Focal Types'),
                        message: __("Available focal types for {0}: {1}").format(
                            frm.doc.college,
                            available.join(", ")
                        ),
                        indicator: 'blue'
                    });
                }
            }
        }
    });
}