// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Company Compact', {
    department: function(frm){
        if(frm.doc.department){
            frappe.call({
                "method": "get_department_details",
                "doc": frm.doc,
                "args": {
                    "department": frm.doc.department
                },
                "callback": function(r) {
                    console.log(r.message)
                    if(r.message){
                        frm.toggle_display('financial_2', r.message[2] > 1);
                        frm.toggle_display('financial_1', r.message[2]);
                        frm.toggle_display('non_financial_1', r.message[3]);
                        frm.toggle_display('non_financial_2', r.message[3] > 1);
                        frm.toggle_display('non_financial_3', r.message[3] > 2);
                        r.message[0].forEach(function(item, index) {
                            frm.fields_dict['financial_'+String(index+1)].df.label = item;
                    
                            // Update the visible DOM now
                            $(frm.fields_dict['financial_'+String(index+1)].wrapper)
                                .find('label.control-label')
                                .text(item);
    
                         });
                        r.message[1].forEach(function(item, index) {
                            frm.fields_dict['non_financial_'+String(index+1)].df.label = item;
                    
                            // Update the visible DOM now
                            $(frm.fields_dict['non_financial_'+String(index+1)].wrapper)
                                .find('label.control-label')
                                .text(item);
                        });
                 }
                }
            })
        }
    },
	// onload_post_render: function(frm) {
	// 	if(frm.doc.type == "Company"){
	// 		console.log(frm.doc.type)
	// 		$('[data-fieldname="financial"] label.control-label').text("Hello");
	// 	}
	// 	$(".form-grid").each(function() {
	// 		// Get all child nodes, filter only text nodes
	// 		var textNode = $(this).contents().filter(function() {
	// 			return this.nodeType === Node.TEXT_NODE && this.textContent.trim() !== "";
	// 		})[0];
		
	// 		// if (textNode && textNode.textContent.trim() === "1. Financial") {
	// 		if (textNode) {
	// 			textNode.textContent = "1. Marketing ";
	// 		}
	// 	});
	// },
    // refresh(frm) {
    //     // Change df so future refreshes know about it
	// 	if(frm.doc.type != "Company"){
	// 		frm.fields_dict['financial'].df.label = "New Label Text";
			
	// 		// Change in DOM immediately
	// 		$(frm.fields_dict['financial'].wrapper)
	// 			.find('label.control-label')
	// 			.text("New Label Text");
	// 	}
    // }
    refresh(frm) {
		frm.set_query('department', function(doc) {
			return {
				filters: {
					"is_department": 1,
					"company": doc.company
				}
			};
		});
        // Get the new value from the category field

        // Build the new label text
        let new_label_1 = ``;
        let new_label_2 = ``;
        let new_label_3 = ``;
        if(frm.doc.type == "Company"){
            new_label_1 = `2.1 Customer Perspective`;
            new_label_2 = `2.2 Innovation and Talent`;
            new_label_3 = `2.3 Risk and Control`;
        }

        // Update definition so Frappe knows about the change
        frm.fields_dict['non_financial_1'].df.label = new_label_1;
        frm.fields_dict['non_financial_2'].df.label = new_label_2;
        frm.fields_dict['non_financial_2'].df.label = new_label_3;

        // Update the visible DOM now
        $(frm.fields_dict['non_financial_1'].wrapper)
            .find('label.control-label')
            .text(new_label_1);
        // Update the visible DOM now
        $(frm.fields_dict['non_financial_2'].wrapper)
            .find('label.control-label')
            .text(new_label_2);
        // Update the visible DOM now
        $(frm.fields_dict['non_financial_3'].wrapper)
            .find('label.control-label')
            .text(new_label_3);
        },
    type(frm) {
        // Get the new value from the category field

        // Build the new label text
        let new_label_1 = ``;
        if(frm.doc.type == "Company"){
            new_label_1 = `2.1 Customer Perspective`;
            frm.toggle_display('financial_1', 1);
            frm.toggle_display('financial_2', 0);
            frm.toggle_display('non_financial_1', 1);
            frm.toggle_display('non_financial_2', 1);
            frm.toggle_display('non_financial_3', 1);
        }
        frm.set_value('financial_1', []);
        frm.set_value('financial_2', []);
        frm.set_value('non_financial_1', []);
        frm.set_value('non_financial_2', []);
        frm.set_value('non_financial_3', []);
        // Update definition so Frappe knows about the change
        frm.fields_dict['non_financial_1'].df.label = new_label_1;

        // Update the visible DOM now
        $(frm.fields_dict['non_financial_2'].wrapper)
            .find('label.control-label')
            .text(new_label_1);
    }
});
