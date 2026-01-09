// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stipend Entry", {
    onload:function(frm){
        if (!frm.doc.posting_date) {
			frm.doc.posting_date = frappe.datetime.nowdate();
		}
    },
	refresh(frm) {
		frm.set_query("student_code",function(){
			return{
				"filters":{
				"company":frm.doc.company
				}
			};
		})
		if (frm.doc.status === "Queued") frm.page.btn_secondary.hide();
        if (frm.doc.docstatus === 0 && !frm.is_new()) {
			frm.page.clear_primary_action();
			frm.add_custom_button(__("Get Students"), function () {
				frm.events.get_student_details(frm);
				
			}).toggleClass("btn-primary", !(frm.doc.student_code || []).length);
		}
		if (
			(frm.doc.students || []).length &&
			!frappe.model.has_workflow(frm.doctype) &&
			!cint(frm.doc.stipend_slip_created) &&
			frm.doc.docstatus != 2
		) {
			if (frm.doc.docstatus == 0 && !frm.is_new()) {
				
				frm.page.clear_primary_action();
				frm.page.set_primary_action(__("Create Stipend Slips"), () => {
					frm.save("Submit").then(() => {
						frm.page.clear_primary_action();
						frm.refresh();
					});
				});
			} else if (frm.doc.docstatus == 1 && frm.doc.status == "Failed") {
		
				frm.add_custom_button(__("Create Stipend Slips"), function () {
					frm.call("create_stipend_slips");
				}).addClass("btn-primary");
			}

		}
		if (frm.doc.docstatus == 1) {
			if (frm.custom_buttons) frm.clear_custom_buttons();
			frm.events.add_context_buttons(frm);
		}

		if (frm.doc.status == "Failed" && frm.doc.error_message) {
			const issue = `<a id="jump_to_error" style="text-decoration: underline;">issue</a>`;
			let process = cint(frm.doc.salary_slips_created) ? "submission" : "creation";

			frm.dashboard.set_headline(
				__("Salary Slip {0} failed. You can resolve the {1} and retry {0}.", [
					process,
					issue,
				]),
			);

			$("#jump_to_error").on("click", (e) => {
				e.preventDefault();
				frm.scroll_to_field("error_message");
			});
		}


	},
    month: function (frm) {
		frm.trigger("set_start_end_dates").then(() => {
			//frm.events.clear_employee_table(frm);
		});
	},
	start_date:function (frm) {
		frm.trigger("check_start_date_range").then(() => {
			//frm.events.clear_employee_table(frm);
		});
	},
	end_date:function (frm) {
		frm.trigger("check_end_date_range").then(() => {
			//frm.events.clear_employee_table(frm);
		});
	},
    set_start_end_dates: function (frm) {
		frappe.call({
			method: "erpnext.student_services.doctype.stipend_entry.stipend_entry.get_start_end_dates",
			args: {
				fiscal_year: frm.doc.fiscal_year,
				month: frm.doc.month,
			},
			callback: function (r) {
				if (r.message) {
					in_progress = true;
					frm.set_value("start_date", r.message.start_date);
					frm.set_value("end_date", r.message.end_date);
				}
			},
		});
	},

	check_start_date_range: function (frm) {
		frappe.call({
			method: "erpnext.student_services.doctype.stipend_entry.stipend_entry.check_start_end_dates",
			args: {
				date_sr:frm.doc.start_date,
				fiscal_year: frm.doc.fiscal_year,
				month: frm.doc.month,
			},
			
		});
	},
	check_end_date_range: function (frm) {
		frappe.call({
			method: "erpnext.student_services.doctype.stipend_entry.stipend_entry.check_start_end_dates",
			args: {
				date_sr:frm.doc.end_date,
				fiscal_year: frm.doc.fiscal_year,
				month: frm.doc.month,
			},
			
		});
	},
    
	 clear_student_table: function(frm) {
        if (frm.doc.students && frm.doc.students.length > 0) {
            frm.clear_table("students");
            frm.refresh_field("students");
        }
    },
    
    get_student_details: function(frm) {
        return frappe.call({
            doc: frm.doc,
            method: "fill_student_details",
            freeze: true,
            freeze_message: __("Fetching students..."),
        }).then((r) => {
            if (r.message > 0) {
                frm.refresh_field("students");
                frm.refresh_field("number_of_students");
                frappe.show_alert({
                    message: __("{0} students added successfully", [r.message]),
                    indicator: 'green'
                });
            }
            frm.scroll_to_field("students");
        });
    },
	create_stipend_slips: function (frm) {
		frm.call({
			doc: frm.doc,
			method: "run_doc_method",
			args: {
				method: "create_stipend_slips",
				dt: "Stipend Entry",
				dn: frm.doc.name,
			},
		});
	},

	add_context_buttons: function (frm) {
		
		if (
			frm.doc.stipend_slip_submitted ||
			(frm.doc.__onload)
		) {
			frm.events.add_bank_entry_button(frm);
		} else if (frm.doc.stipend_slip_created && frm.doc.status !== "Queued") {
			frm.add_custom_button(__("Submit Stipend Slip"), function () {
				submit_stipend_slip(frm);
			}).addClass("btn-primary");
		} else if (!frm.doc.salary_slips_created && frm.doc.status === "Failed") {
			frm.add_custom_button(__("Create Stipend Slips"), function () {
				frm.trigger("create_salary_slips");
			}).addClass("btn-primary");
		}
	},

	add_bank_entry_button: function (frm) {
		frm.call("has_bank_entries").then((r) => {
			if (!r.message.has_bank_entries) {
				frm.add_custom_button(__("Make Bank Entry"), function () {
					make_bank_entry(frm);
				}).addClass("btn-primary");
			}
		});
	},
});

const submit_stipend_slip = function (frm) {
	frappe.confirm(
		__(
			"This will submit Stipend Slips and create accrual Journal Entry. Do you want to proceed?",
		),
		function () {
			frappe.call({
				method: "submit_stipend_slips",
				args: {},
				doc: frm.doc,
				freeze: true,
				freeze_message: __("Submitting Stipend Slips and creating Journal Entry..."),
				 callback: function(r) {
                    // Refresh the form to update document state after successful submission
                    if (!r.exc) {
                        frm.refresh();
                        frappe.show_alert({
                            message: __('Stipend slips submitted successfully'),
                            indicator: 'green'
                        });
                    }
                }
			});
		},
		function () {
			if (frappe.dom.freeze_count) {
				frappe.dom.unfreeze();
			}
		},
	);
};
let make_bank_entry = function (frm) {
	const doc = frm.doc;
	return frappe.call({
		method: "run_doc_method",
		args: {
			method: "make_bank_entry",
			dt: "Stipend Entry",
			dn: frm.doc.name,
		},
		callback: function () {
			// frappe.set_route("List", "Journal Entry", {
			// 	"Journal Entry Account.reference_name": frm.doc.name,
			// });
			frappe.set_route(
				'List', 'Journal Entry', {"reference_type": frm.doc.doctype, "reference_name": frm.doc.name}
			);
		},
		freeze: true,
		freeze_message: __("Creating Payment Entries......"),
	});
};