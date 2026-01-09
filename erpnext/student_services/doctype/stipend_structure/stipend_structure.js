// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stipend Structure", {
    onload: function (frm) {
		frm.set_query("stipend_component", "earnings", function () {
			return {
				filters: { component_type: "earning" },
				// query: "hrms.payroll.doctype.salary_structure.salary_structure.get_salary_component",
			};
		});
		frm.set_query("stipend_component", "deductions", function () {
			return {
				filters: { component_type: "deduction" },
				// query: "hrms.payroll.doctype.salary_structure.salary_structure.get_salary_component",
			};
		});
	},

	refresh(frm) {
        frm.set_query("student_code",function(){
			return{
				"filters":{
				"company":frm.doc.company
				}
			};
		})

	},
    eligible_for_rent: function(frm) {
        update_deductions_only(frm);
    },
    eligible_for_mess_fees: function(frm) {
        update_deductions_only(frm);
    }
});

frappe.ui.form.on('Stipend Details', {
    stipend_component: function(frm, cdt, cdn) {
        let child_row = locals[cdt][cdn];
        
        // Only update earnings if stipend component changes in earnings table
        if (child_row.stipend_component === 'Stipend') {
            update_earnings_only(frm);
        }
    }
});

function update_deductions_only(frm) {
    frappe.call({
        method: "update_stipend_structure",
        doc: frm.doc,
        args: {
            "update_type": "deductions"  // Only update deductions
        },
        callback: function(r) {
            frm.refresh_fields();
        }
    });
}

function update_earnings_only(frm) {
    frappe.call({
        method: "update_stipend_structure",
        doc: frm.doc,
        args: {
            "update_type": "earnings",  // Only update earnings
            "save": 1,
        },
        callback: function(r) {
            frm.refresh_fields();
        }
    });
}