// holitics-object-dialog-properties.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project

// Includes all js functions needed for object properties dialog.

function _populate_properties(obj_id, data, property_items, ui_models, enum_values, state_values) {
	
	var content = '';
	
	property_items.forEach(function(item,index) {
	
		var attributes = item.attributes;
		var valid_enum_values = null;
		
		// alert(attributes);
		
		if (attributes === undefined || attributes == null) {
			// do not show this property
		} else {
			var show_in_ui = attributes[0].show_in_ui;
			var value_enum = attributes[0].value_enum;
			
			if (show_in_ui === undefined || show_in_ui == "false") {
		
				// do not show this property
		
			} else {
			
				if (value_enum !== undefined) {
					valid_enum_values = enum_values[value_enum];
				}
				
				content = content + _build_ui_property(item, obj_id, ui_models, valid_enum_values, state_values);
			}
		}
		
	});	// end for each for data

	return content;

}

var populate_properties = function(obj_id, data) {

	// these are lists
	var properties = data['data'][0]['properties'];
	var enum_values = data['data'][0]['enum_values'];
	
	var property_items = _get_sorted_list_by_name(properties);

	var ui_models = {}; //data['data'][0]['ui_models'];
	var state_values = {}; //data['data'][0]['state_values'];
	var buttons_added = {};
	var content = "<form id='form_update_properties'><input type='hidden' id='form_object_id' value='" + obj_id + "'>";
	
	// get a grouped, sorted dictionary of lists of actions
	groups = _get_grouped_lists(property_items, 'name');
	
	for (var key in groups) {

		content = content + "<h6 class='dropdown-header'><center>-- " + key + " properties --</center></h6>";
	
		// populate all the properties for this group
		content = content + _populate_properties(obj_id, data, groups[key], ui_models, enum_values, state_values);

	}
	
	content = content + '</form>';

	_launch_modal_dialog("Properties", "property_dialog", content, "Save", clicked_modal_save_properties_button, false);
	
}


function _build_ui_property(item, obj_id, ui_models, enum_values, state_values) {

	// create the property

	if (item.name.startsWith('_')) {
		return "";
	}
	
	var value = item.value;
	if (value == null) {
		value = "";
	}

	var combo_box = false;
	
	if (enum_values !== undefined && enum_values != null) {
		combo_box = true;
	}
	
	var field_type = "text";
	
	if (item.name.startsWith('password')) {
		field_type = "password";
	}
	
	var prop = "<div class='form-group row'>";
	prop = prop + "		<label class='col-sm-5 col-form-label' for='form_" + item.name + "'>" + item.name + "</label>";
	prop = prop + "		<div class='col-sm-7'>";
	
	if (combo_box) {
		prop = prop + "			<select class='form-control form-control-sm' id='form_" + item.name + "' name='" + item.name + "'>";
		for (var key in enum_values){
			var enum_value = enum_values[key];
			var selected = "";
			if (enum_value == value) {
				selected = " selected ";
			} 		
			prop = prop + "				<option value='" + enum_values[key] + "' " + selected + ">" + key + "</option>";
		}
		prop = prop + "			</select>";
	} else {
		prop = prop + "			<input type='" + field_type + "' class='form-control form-control-sm' id='form_" + item.name + "' name='" + item.name + "' placeholder='' value='" + value + "'>";
	}
	
	prop = prop + "			<small id='" + item.name + "_help' class='text-muted'>" + item.description + "</small>";
    prop = prop + "		</div>";
    prop = prop + "</div>";
  
	return prop;
	
}

function clicked_modal_save_properties_button() {

	// remove the modal dialog
	$('#centered_modal_dialog').modal('hide');

	var form_data = {};
	var obj_id = $('#form_object_id').val();
	
	form_data["object_id"] = obj_id;
	
	// now fill in with fields from the form
	var elements = $('#form_update_properties')[0].elements;

	for (var i = 0, element; element = elements[i++];) {
		form_data[element.name] = element.value;
	}

	// submit the FORM
    $.ajax({
        url: '/update_object_properties',
        type: 'POST',
        data: form_data,
        success: function(msg)
        {
        	response = msg['data'][0];
       		// TODO - implement TOAST for both success and fail!!
        	if (response['status']==0) {
	       		// refresh the object dialog
				refresh_object_dialog(obj_id);
        	} else {
        		alert("Error while updating object properties: " + response['error']);
        	}
        }
    });

}
