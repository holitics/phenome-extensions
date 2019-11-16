// holitics-object-dialog-relations.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project

// Includes all js functions needed for object relations dialog.

var _populate_relations_subclasstype_select = function(data) {

	var content = '<option value="" selected>Type of Object</option>';
	
	// populate the dropdown
	var dropdown = $("#form_subclasstype_filter");
	
	data.forEach(function(item,index) {
		var classtype_key = item.id;
		var classtype_id = item.value[0]['value'];
		var item_description = item.value[0]['description'];
		content = content + "<option value='" + classtype_id + "'>" + item_description + "</option>";
	});
	
	dropdown.html(content);
   	
}

function _add_to_relation_types(type, value) {
	_relation_types[type] = value;
	_relation_types_rev[value] = type;
}

function retrieve_relation_enum_data() {

	_relation_types = {};
	_relation_types_rev = {};

	// build url		
	var url = '/api/v1/get_enum_by_id/_RELATION_TYPES_/0';
	
	$.getJSON(url, function(data) {
		relation_types = data['data'][0]['_RELATION_TYPES_'];
		for (var type in relation_types) {
			_add_to_relation_types(type, relation_types[type]);
		}
	});
	
}

function _populate_relations_power_section(obj_id) {

	// first empty the div
	var div_relations_power = $('#relations_power_source');
	div_relations_power.empty();

	if (object_details['power_state'] == 0) {
	
		// this object is not connected to a power source
		
		var content = "<h6 class='dropdown-header'>Power Source<span class='badge badge-warning' style='float:right;'>Not Configured</span></h6>";
		var template = $("#relation_dialog_add_power_template").html();
		
		// add template to the content
		content = content + template;
		
		// add inline help and extra "HR" line to separate from content below
		content = content + '<center><span class="help-inline error"></span></center><HR>';
	
		// insert into the div
		div_relations_power.html(content);
		
		// now populate with the potential power sources
		_populate_object_select_by_classtype('POWER_DISTRIBUTION_UNIT', '_relation_id', 'Choose power source');
	
		// attach to the submit button and handle callbacks with the standard form validation
		attach_ajax_submit_listener('form_add_relation', do_submit_callback_success_add_relation, do_submit_callback_error);
	
	}

}

function _related_object_changed(select_object) {

 	// get the index of the selected option 
 	var idx = select_object.selectedIndex; 
 	
 	// get the value of the selected option 
 	var classtype_id = select_object.options[idx].value; 

	if (classtype_id != "") {
		// make sure modal button is enabled
		$("#centered_modal_dialog_button_confirm").removeClass('disabled');	
	}

}


function _relation_type_changed(select_object) { 
 	
 	// get the index of the selected option 
 	var idx = select_object.selectedIndex; 
 	
 	// get the value of the selected option 
 	var rel_type_id = select_object.options[idx].text; 
 	
} 

function _classtype_changed(select_object) { 
 	
 	// get the index of the selected option 
 	var idx = select_object.selectedIndex; 
 	
 	// get the value of the selected option 
 	var classtype_id = select_object.options[idx].value; 
 	
	_populate_object_select_by_subclasstype(classtype_id, 'form_relation_id', 'Choose related object');

} 

function _populate_relations_add_new_button(obj_id) {

	var div_relations_add = $('#relations_add_new');
	div_relations_add.innerHtml = "";
	div_relations_add.html("<center><button type='button' class='btn btn-primary' onclick='javascript:_populate_relations_add_new_section(" + obj_id + ");'>Add Related Object</button></center>");

}

function _populate_relation_type_select() {

	var dropdown = $("#form_relation_type");
	var content = '<option value="" selected>Type of Relationship</option>';
	for (var type in _relation_types) {
		content = content + "<option value='" + _relation_types[type] + "'>" + type + "</option>";
    }
    dropdown.html(content);

}

function _populate_relations_add_new_section(obj_id) {
	
	// this function clears the modal and creates an "add new" relation dialog section
	var modal = $('#centered_modal_dialog');
	var body_content_structure = "<div id='relations_add_new'></div>";
	modal.find('.modal-body').html(body_content_structure);

	var div_relations_add = $('#relations_add_new');
	div_relations_add.empty();

	// now build the add_new section
	var template = $("#relation_dialog_add_new").html();

	// add inline help to template
	var content = template + '<center><span class="help-inline error"></span></center>';
	
	// insert into the div
	div_relations_add.html(content);

	// make sure modal button is disabled
	$("#centered_modal_dialog_button_confirm").addClass('disabled');

	// populate the relation type dropdown
	_populate_relation_type_select();		

	// populate the subclasstypes dropdown (passing in the callback fn)
	_retrieve_subclasstypes(_populate_relations_subclasstype_select);

	// launch but do not send content, we are implementing content in async ajax
	// we will handle form validation and submission using the clicked_modal_add_relation_button() method
	_launch_modal_dialog("Add Relationship", "relations_dialog", null, "Add", clicked_modal_add_relation_button, false);

}

function _launch_delete_relation(obj_id, rel_id, rel_type_id) {

	var r = confirm("Remove related object?");
	if (r == false) {
		return;
	}

	// delete this relation, then reload the relations dialog
	var url = '/api/v1/delete_relation/' + obj_id + '/' + rel_id + '/' + rel_type_id + '/0';

	$.getJSON(url, function(data) {
		// if successful
		if (rel_type_id==1000) {
			if (object_details !== undefined) {
				object_details['power_state'] = 0;
				draw_canvas_icons(0, obj_id);
			}
		}
		populate_relations(obj_id);
	});

	
}

function _populate_relations_list_section(obj_id) {

	// empty relations list
	$('#relations_list').innerHtml = "";
	
	// build url to retrieve the relations
	var url = '/api/v1/get_relations_by_object_id/' + obj_id + '/0';
	var relations = null;

	// separate section from other section
	var content = "<HR>";
	
	// retrieve relations per OBJECT
	$.getJSON(url, function(data) {
		if (data != null) {	
			relations = data['data'][0];
			
			for (var relation_group in relations) {
				content = content + "<h6 class='dropdown-header'><center>-- " + relation_group + " --</center></h6>";
				group = relations[relation_group];
				for (var relation_obj_id in group) {
					var object = group[relation_obj_id];
					model = object['object_details']['model_name'];
					name = object['object_details']['name'];
					details = object['relation_details']['details'];
					relation_type_id = object['relation_details']['relation_type'];
					content = content + "<div class='obj_dialog_relation_item'><a href='javascript:_launch_object_dialog_modal(" + relation_obj_id + ",\"" + name + "\")'>" + name + "</a>";
					content = content + "<a style='float:right;padding:7px;' href='javascript:_launch_delete_relation(" + obj_id + ",\"" + relation_obj_id + "\",\"" + relation_type_id + "\")' class='badge badge-light'>Remove</a>";
					
					if (details !== null) {
						var div_details = "<div style='float:right;padding-right:20px;'>";
						if (relation_type_id==1000 && details !== null && details.indexOf('outlet')==-1) { 
							content = content + div_details + "outlet=" + details + "</div>";
						} else {
							content = content + div_details + details + "</div>";
						}
					}
					
					content = content + "</div>";
					
				}
			}
			var div_relations_list = $('#relations_list');
			div_relations_list.html(content);
		}
	});
	
}

var populate_relations = function(obj_id) {

	if (_relation_types == null) {
		retrieve_relation_enum_data();
	}

	// first prepare the modal body content div
	var modal = $('#centered_modal_dialog');
	var body_content_structure = "<div id='relations_power_source'></div>";
	body_content_structure = body_content_structure + "<div id='relations_add_new'></div>";
	body_content_structure = body_content_structure + "<div id='relations_list'></div>";
	modal.find('.modal-body').html(body_content_structure);

	var body = modal.find('.modal-body');
	body.empty();
	body.html(body_content_structure);

	// build the power_source section
	if (object_details['powered_object'] == 1) {
		_populate_relations_power_section(obj_id);	
	}

	// build the standard section
	_populate_relations_add_new_button(obj_id);

	// build the list section	
	_populate_relations_list_section(obj_id);
		
	// launch but do not send content, we are implementing content in async ajax
	_launch_modal_dialog("Relations", "relations_dialog", null, null, null, false);
	
}


function clicked_modal_add_relation_button() {

	var modal_button = $('#centered_modal_dialog_button_confirm');

	// make sure required fields are implemented

	var src_obj_id = $('#form_object_id').val();	
	var relation_type = $('#form_relation_type').val();
	var dest_obj_id = $('#form_relation_id').val();
	var error_msg = '';

	if (modal_button.hasClass('disabled')) {
		error_msg = "Please fill out the fields to add a relation";
	}

	if (relation_type == "") {
		error_msg = "Please specify the TYPE of relationship";
	}
	
	if (dest_obj_id == "") {
		error_msg = "Please specify the OBJECT to relate";
	}

	if (src_obj_id == dest_obj_id) {
		error_msg = "Cannot create relationship to oneself";
	}
	
	if (error_msg != "") {
		var display_msg = "<div class='alert alert-danger' role='alert'>" + error_msg + "</div>";
		_display_message(error_msg, display_msg);
		return;
	}

	// alert("clicked, rel_type=" + relation_type + ", object_id=" + src_obj_id + ", dest_id:" + dest_obj_id);

	// form must be valid, now submit
	var submit_button = $('#form_add_relation_submit_button');
	var form = $('#form_add_relation');
	
	submit_button.button('loading');
	
	// submit the form, add the relation	

	$.ajax({
	  url: form.attr('action'),
	  type: form.attr('method'),
	  dataType: 'json',
	  data: form.serialize(),
	  success: function(data, text, xhr){
		submit_button.button('reset');
		do_submit_callback_success_add_relation(data, text, xhr);
		refresh_object_dialog(src_obj_id);
	  },
	  error:function(data, text, error){
		submit_button.button('reset');
		do_submit_callback_error(data, text, error);
	  }
	});

}