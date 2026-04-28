// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.setup");
erpnext.setup.EmployeeController = class EmployeeController extends frappe.ui.form.Controller {
	setup() {
		this.frm.fields_dict.user_id.get_query = function (doc, cdt, cdn) {
			return {
				query: "frappe.core.doctype.user.user.user_query",
				filters: { ignore_user_type: 1 },
			};
		};
		this.frm.fields_dict.reports_to.get_query = function (doc, cdt, cdn) {
			return { query: "erpnext.controllers.queries.employee_query" };
		};
	}

	refresh(frm) {
		if (!frm.dashboard || !frm.dashboard.wrapper) return;

		let section = $(frm.dashboard.wrapper)
			.find('.form-dashboard-section.form-links');

		let head = section.find('.section-head');
		let body = section.find('.section-body');

		if (head.length) {
			head.addClass('collapsed');
			body.hide();
		}
		erpnext.toggle_naming_series();
	}
};

frappe.ui.form.on("Employee", {
	company: function(frm) {

		// clear dependent fields when company changes
		frm.set_value("branch", null);
		frm.set_value("department", null);
		frm.set_value("division", null);
		frm.set_value("section", null);
		frm.set_value("unit", null);

	},
	setup: function(frm) {

		frm.set_query("branch", function() {
			if (!frm.doc.company) {
				frappe.msgprint("Please select college first");
				return;
			}

			return {
				filters: {
					company: frm.doc.company,
					disabled:0
				}
			};
		});
		frm.set_query("business_activity", function() {
			if (!frm.doc.company) {
				frappe.msgprint("Please select college first");
				return;
			}

			return {
				filters: {
					company: frm.doc.company,
					is_disabled:0
				}
			};
		});

		// frm.set_query("second_approver",function(){
		// 	if (!frm.doc.company) {
		// 		frappe.msgprint("Please select college first");
		// 		return;
		// 	}

		// 	return{
		// 		filters:{
		// 			company:frm.doc.company,
		// 			status:"Active"
		// 		}
		// 	}
		// })

    
		// frm.set_query("second_approver", function () {
        //     let filters = {
        //         status: "Active"
        //     };
        //     if (frm.doc.designation !== "President") {

        //         if (!frm.doc.company) {
        //             frappe.msgprint("Please select college first");
        //             return;
        //         }

        //         filters.company = frm.doc.company;
        //     }

        //     return {
        //         filters: filters
        //     };
        // });

		frm.set_query("second_approver", function () {

            // If President → only Vice Chancellor allowed
            if (frm.doc.designation === "President") {
                return {
                    filters: {
                        designation: "Vice Chancellor"
                    }
                };
            }

            // For others → require company first
            if (!frm.doc.company) {
                frappe.msgprint("Please select college first");
                return;
            }

            return {
                filters: {
                    status: "Active",
                    company: frm.doc.company
                }
            };
        });

		
		frm.set_query("department", function () {
			return {
				filters: {
					company: frm.doc.company,
					is_department:1


				},
			};
		});
		frm.set_query("division", function () {
			return {
				filters: {
					company: frm.doc.company,
					is_division:1,
					parent_department:frm.doc.department


				},
			};
		});
		frm.set_query("section", function () {
			return {
				filters: {
					company: frm.doc.company,
					is_section:1,
					parent_department:frm.doc.division


				},
			};
		});
		frm.set_query("unit", function () {
			return {
				filters: {
					company: frm.doc.company,
					is_unit:1,
					parent_department:frm.doc.section


				},
			};
		});	
	

	},

	prefered_contact_email: function (frm) {
		frm.events.update_contact(frm);
	},

	personal_email: function (frm) {
		frm.events.update_contact(frm);
	},

	company_email: function (frm) {
		frm.events.update_contact(frm);
	},

	user_id: function (frm) {
		frm.events.update_contact(frm);
	},

	update_contact: function (frm) {
		var prefered_email_fieldname = frappe.model.scrub(frm.doc.prefered_contact_email) || "user_id";
		frm.set_value("prefered_email", frm.fields_dict[prefered_email_fieldname].value);
	},

	status: function (frm) {
		return frm.call({
			method: "deactivate_sales_person",
			args: {
				employee: frm.doc.employee,
				status: frm.doc.status,
			},
		});
	},

	create_user: function (frm) {
		if (!frm.doc.prefered_email) {
			frappe.throw(__("Please enter Preferred Contact Email"));
		}
		frappe.call({
			method: "erpnext.setup.doctype.employee.employee.create_user",
			args: {
				employee: frm.doc.name,
				email: frm.doc.prefered_email,
			},
			freeze: true,
			freeze_message: __("Creating User..."),
			callback: function (r) {
				frm.reload_doc();
			},
		});
	},
});

cur_frm.cscript = new erpnext.setup.EmployeeController({
	frm: cur_frm,
});

frappe.tour["Employee"] = [
	{
		fieldname: "first_name",
		title: "First Name",
		description: __(
			"Enter First and Last name of Employee, based on Which Full Name will be updated. IN transactions, it will be Full Name which will be fetched."
		),
	},
	{
		fieldname: "company",
		title: "Company",
		description: __("Select a Company this Employee belongs to."),
	},
	{
		fieldname: "date_of_birth",
		title: "Date of Birth",
		description: __(
			"Select Date of Birth. This will validate Employees age and prevent hiring of under-age staff."
		),
	},
	{
		fieldname: "date_of_joining",
		title: "Date of Joining",
		description: __(
			"Select Date of joining. It will have impact on the first salary calculation, Leave allocation on pro-rata bases."
		),
	},
	{
		fieldname: "reports_to",
		title: "Reports To",
		description: __(
			"Here, you can select a senior of this Employee. Based on this, Organization Chart will be populated."
		),
	},
];
