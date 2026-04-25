// frappe.treeview_settings["Department"] = {
// 	ignore_fields: ["parent_department"],
// 	get_tree_nodes: "erpnext.setup.doctype.department.department.get_children",
// 	add_tree_node: "erpnext.setup.doctype.department.department.add_node",


// 	filters: [
// 		{
// 			fieldname: "company",
// 			fieldtype: "Link",
// 			options: "Company",
// 			label: __("College"),
// 			default: function() {
// 				// For employees, this will be set by onload
// 				// For admins, try to get from defaults
// 				var user = frappe.session.user
// 				var employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
// 				var user_roles = frappe.user_roles;
// 				var is_admin = user_roles.includes("System Manager") || user_roles.includes("Administrator");
				
// 				if (is_admin) {
					
// 				}
// 				return ""; // Will be set in onload
// 			}
// 		},
// 	],
// 	breadcrumb: "HR",
// 	root_label: "All Departments",
// 	get_tree_root: true,
// 	menu_items: [
// 		{
// 			label: __("New Department"),
// 			action: function () {
// 				frappe.new_doc("Department", true);
// 			},
// 			condition: 'frappe.boot.user.can_create.indexOf("Department") !== -1',
// 		},
// 	],
	
// 	onload: function (treeview) {
// 		treeview.make_tree();
// 	},
// 	onrender: function (node) {
// 		get_employee_count(node);
// 	}
	
// };
// function get_employee_count(node) {
	
	
// 	frappe.call({
// 		method: "erpnext.setup.doctype.department.department.get_employee_count",
// 		args: { department_name: node.data.value },
// 		callback: function (r) {
// 			if (!r.message) return;

// 			let format_string = "";

// 			// Type badges
// 			if (r.message.is_division) {
// 				format_string += `<span class="badge badge-light" style="font-size:xx-small; margin-left:5px; border-right:1px solid grey; border-radius:3px 0px 0px 3px; background-color:#e5c9f7">Division</span>`;
// 			}
// 			if (r.message.is_department) {
// 				format_string += `<span class="badge badge-light" style="font-size:xx-small; margin-left:5px; border-right:1px solid grey; border-radius:3px 0px 0px 3px; background-color:#b3f0ff">Department</span>`;
// 			}
// 			if (r.message.is_section) {
// 				format_string += `<span class="badge badge-light" style="font-size:xx-small; margin-left:5px; border-right:1px solid grey; border-radius:3px 0px 0px 3px; background-color:#d4edda">Section</span>`;
// 			}
// 			if (r.message.is_unit) {
// 				format_string += `<span class="badge badge-light" style="font-size:xx-small; margin-left:5px; border-right:1px solid grey; border-radius:3px 0px 0px 3px; background-color:#ffe6b3">Unit</span>`;
// 			}

// 			if (r.message.employee_count > 0) {
// 	format_string += `<span class="badge badge-light"
// 		style="font-size:xx-small; border-radius:0px 3px 3px 0px; background-color:gold">
// 		Employee:${r.message.employee_count}
// 	</span>`;
// }
// 			// Approver badge (optional)
// 			if (r.message.approver) {
// 				format_string += `<span class="badge badge-light" style="font-size:xx-small; margin-left:5px; border-radius:3px; background-color:#f7d9e5">Approver:${r.message.approver}</span>`;
// 			}

// 			// Insert after tree link
// 			node.$tree_link.after(format_string);
// 		}
// 	});
// }

frappe.treeview_settings["Department"] = {
	ignore_fields: ["parent_department"],
	get_tree_nodes: "erpnext.setup.doctype.department.department.get_children",
	add_tree_node: "erpnext.setup.doctype.department.department.add_node",
	filters: [
		{
			fieldname: "company",
			fieldtype: "Link",
			options: "Company",
			label: __("College"),
		},
	],
	breadcrumb: "HR",
	root_label: "All Departments",
	get_tree_root: true,
	menu_items: [
		{
			label: __("New Department"),
			action: function () {
				frappe.new_doc("Department", true);
			},
			condition: 'frappe.boot.user.can_create.indexOf("Department") !== -1',
		},
	],
	onload: function (treeview) {
		// Get company from employee linked to current user
		frappe.call({
			method: "erpnext.setup.doctype.department.department.get_user_company",
			callback: function(r) {
				if (r.message) {
					// Set the company filter with employee's company
					treeview.page.fields_dict.company.set_value(r.message);
					
					// Optional: Make it read-only for employees
					var user_roles = frappe.user_roles;
					var is_admin = user_roles.includes("System Manager") || user_roles.includes("Administrator");
					if (!is_admin) {
						treeview.page.fields_dict.company.df.read_only = 1;
						treeview.page.fields_dict.company.refresh();
					}
				}
				treeview.make_tree();
			}
		});
	},
	onrender: function (node) {
		get_employee_count(node);
	}
};

function get_employee_count(node) {
	frappe.call({
		method: "erpnext.setup.doctype.department.department.get_employee_count",
		args: { department_name: node.data.value },
		callback: function (r) {
			if (!r.message) return;

			let format_string = "";

			// Type badges
			if (r.message.is_division) {
				format_string += `<span class="badge badge-light" style="font-size:xx-small; margin-left:5px; border-right:1px solid grey; border-radius:3px 0px 0px 3px; background-color:#e5c9f7">Division</span>`;
			}
			if (r.message.is_department) {
				format_string += `<span class="badge badge-light" style="font-size:xx-small; margin-left:5px; border-right:1px solid grey; border-radius:3px 0px 0px 3px; background-color:#b3f0ff">Department</span>`;
			}
			if (r.message.is_section) {
				format_string += `<span class="badge badge-light" style="font-size:xx-small; margin-left:5px; border-right:1px solid grey; border-radius:3px 0px 0px 3px; background-color:#d4edda">Section</span>`;
			}
			if (r.message.is_unit) {
				format_string += `<span class="badge badge-light" style="font-size:xx-small; margin-left:5px; border-right:1px solid grey; border-radius:3px 0px 0px 3px; background-color:#ffe6b3">Unit</span>`;
			}

			if (r.message.employee_count > 0) {
				format_string += `<span class="badge badge-light"
					style="font-size:xx-small; border-radius:0px 3px 3px 0px; background-color:gold">
					Employee:${r.message.employee_count}
				</span>`;
			}
			
			if (r.message.approver) {
				format_string += `<span class="badge badge-light" style="font-size:xx-small; margin-left:5px; border-radius:3px; background-color:#f7d9e5">Approver:${r.message.approver}</span>`;
			}

			node.$tree_link.after(format_string);
		}
	});
}