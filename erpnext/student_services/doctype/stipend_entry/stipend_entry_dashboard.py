def get_data():
	return {
		"fieldname": "stipend_entry",
		"non_standard_fieldnames": {
			"Journal Entry": "reference_name",
			"Payment Entry": "reference_name",
		},
		"transactions": [{"items": ["Stipend Slip","Journal Entry"]}],
	}
