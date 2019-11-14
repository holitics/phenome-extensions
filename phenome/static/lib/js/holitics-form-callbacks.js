// holitics-form-callbacks.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project
//
// some callback methods

function do_submit_callback_error(data, text, error) {

	var error_msg = 'Unknown Error';
		
	try {	
		status = data.responseJSON.status;
		error = data.responseJSON.error;
		error_msg = "ERROR [" + status + "] - " + error;
	} catch (err) {
		error_msg = err.message;	
	}
	
	var display_msg = "<div class='alert alert-danger' role='alert'>" + error_msg + "</div>";

	_display_message(error_msg, display_msg);

}

function do_submit_callback_success(data, text) {

	var display_msg = "<div class='alert alert-success' role='alert'>Created [" + data.data['name'] + ", ID=" + data.data['id'] + "]</div>";
	
	_display_message(display_msg, display_msg);

}

function do_submit_callback_success_add_relation(data, text) {

	var object_id = data.data[0]['object_id']
	var relation_object_id = data.data[0]['relations'][0]['object_id_to']
	
	var display_msg = "<div class='alert alert-success' role='alert'>Created relation from [" + object_id + "] to [" + relation_object_id + "]</div>";

	// first remove the add_relation form
	var element = document.getElementById('form_add_relation');
	var parent_node = null;
	if (element !== undefined) {
		var parent_node = element.parentNode;
		parent_node.removeChild(element);
	}

	// now refresh the top of the dialog
	if (parent_node !== null && parent_node.id == 'relations_power_source') {
		// pretend we know the power state so we don't get the "not configured" section again
		if (object_details !== undefined) {
			object_details['power_state'] = 2;
			draw_canvas_icons(2, object_id);
		}
		_populate_relations_power_section(object_id);
	} else {
		_populate_relations_add_new_section(object_id);
	}

	// display the message
	_display_message(display_msg, display_msg);
		
	// refresh the current relations
	_populate_relations_list_section(object_id);
	
}
