// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("project", "cost_center", "cost_center");

frappe.ui.form.on('Asset Movement', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__('Accounting Ledger'), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		}
	},
	
	setup: (frm) => {
		frm.set_query("to_employee", "assets", (doc) => {
			return {
				filters: {
					company: doc.company
				}
			};
		})
		frm.set_query("from_employee", "assets", (doc) => {
			return {
				filters: {
					company: doc.company
				}
			};
		})
		frm.set_query("reference_name", (doc) => {
			return {
				filters: {
					company: doc.company,
					docstatus: 1
				}
			};
		})
		frm.set_query("reference_doctype", () => {
			return {
				filters: {
					name: ["in", ["Purchase Receipt", "Purchase Invoice"]]
				}
			};
		}),
		frm.set_query("asset", "assets", () => {
			return {
				filters: {
					status: ["not in", ["Draft", "Sold"]]
				}
			}
		})
	},
	onload: (frm) => {
		frm.trigger('set_required_fields');
	},

	purpose: (frm) => {
		frm.trigger('set_required_fields');
	},

	set_required_fields: (frm, cdt, cdn) => {
		let fieldnames_to_be_altered;
		if (frm.doc.purpose === 'Transfer') {
			fieldnames_to_be_altered = {
				target_cost_center: { read_only: 0, reqd: 0 },
				source_cost_center: { read_only: 1, reqd: 1 },
				from_employee: { read_only: 1, reqd: 0 },
				to_employee: { read_only: 0, reqd: 1 }
			};
		}
		else if (frm.doc.purpose === 'Receipt') {
			fieldnames_to_be_altered = {
				target_cost_center: { read_only: 0, reqd: 1 },
				source_cost_center: { read_only: 1, reqd: 0 },
				from_employee: { read_only: 0, reqd: 1 },
				to_employee: { read_only: 1, reqd: 0 }
			};
		}
		else if (frm.doc.purpose === 'Issue') {
			fieldnames_to_be_altered = {
				target_cost_center: { read_only: 1, reqd: 0 },
				source_cost_center: { read_only: 1, reqd: 1 },
				from_employee: { read_only: 1, reqd: 0 },
				to_employee: { read_only: 0, reqd: 1 }
			};
		}
		if (fieldnames_to_be_altered) {
			Object.keys(fieldnames_to_be_altered).forEach((fieldname) => {
				let property_to_be_altered = fieldnames_to_be_altered[fieldname];
				Object.keys(property_to_be_altered).forEach((property) => {
					let value = property_to_be_altered[property];
					frm.fields_dict["assets"].grid.update_docfield_property(fieldname, property, value);
				});
			});
			frm.refresh_field("assets");
		}
	},
	get_asset: function(frm){
		get_asset_list(frm);
	},
	to_employee:function(frm){
		if(cint(frm.doc.to_single) == 1){
			frm.doc.assets.map(v=>{
				v.to_employee = frm.doc.to_employee
			})
			frm.refresh_field("assets")
		}
	}
});

function get_asset_list(frm){
	
	frappe.call({
		method:"get_asset_list",
		doc: frm.doc,
		callback: function (){
			frm.refresh_field("assets")

		}
	});
	
}

frappe.ui.form.on('Asset Movement Item', {
	asset: function(frm, cdt, cdn) {
		const asset_name = locals[cdt][cdn].asset;
		if (asset_name){
			frappe.db.get_doc('Asset', asset_name).then((asset_doc) => {
				if(asset_doc.cost_center ) frappe.model.set_value(cdt, cdn, 'source_cost_center', asset_doc.cost_center);
				if(asset_doc.custodian) frappe.model.set_value(cdt, cdn, 'from_employee', asset_doc.custodian);
				if(asset_doc.custodian_name) frappe.model.set_value(cdt, cdn, 'from_employee_name', asset_doc.custodian_name);
			}).catch((err) => {
			});
		}
	}
});

// frappe.ui.form.on('Asset Movement Item', {  
//     refresh: function(frm) {  
//         frm.fields_dict['Asset'].grid.get_field('cost_center').get_query = function(doc) {  
//             return {  
//                 filters: {  
//                     'to_employee': doc.to_employee // replace with your filtering criteria  
//                 }  
//             };  
//         };  
//     }  
// });

// frappe.ui.form.on('Asset Movement Item', {  
//     refresh: function(frm) {  
//         frm.fields_dict['Asset'].grid.get_field('to_employee').get_query = function(doc) {  
//             return {  
//                 filters: {  
//                     'to_employee': doc.to_employee // replace with your filtering criteria  
//                 }  
//             };  
//         };  
//     }  
// });




// frappe.ui.form.on('Sales Invoice', {  
//     refresh: function(frm) {  
//         frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc) {  
//             return {  
//                 filters: {  
//                     'docstatus': 1 // Adjust filter according to your needs  
//                 }  
//             };  
//         };  

//         frm.fields_dict['items'].grid.get_field('item_code').on_change = function() {  
//             let selected_item = this.get_value();  

//             frappe.call({  
//                 method: "frappe.client.get",  
//                 args: {  
//                     doctype: "Batch",  
//                     name: selected_item  
//                 },  
//                 callback: function(data) {  
//                     if (data.message) {  
//                         // Assuming you want to set expiry date to 'expiry_date' field  
//                         let expiry_date = data.message.expiry_date;  
//                         frm.fields_dict['items'].grid.get_selected_item().expiry_date = expiry_date;  
//                         frm.refresh_field('items');  
//                     }  
//                 }  
//             });  
//         };  
//     }  
// });












