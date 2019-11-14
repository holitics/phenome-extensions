// holitics-dialog-common.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project
//
// Common dialog functions for Holitics API


function build_object_dialog(obj_id) {

	// first clear out any MODAL content just in case an object dialog is already
	modal = $('#centered_modal_dialog');
	modal.find('.modal-body').html("");

	// create the DIV the ajax request will be loading the dialog into
	html = '	<div class="dialog-content-container dialog-content" id="objectdialog_' + obj_id +'">';
	html = html + '</div>';

	// build the arguments for the /object_dialog/ API call
	var url_args = obj_id + '/' + object_dialog_header_only + '/' + object_dialog_show_details;

	// create the script that will load the ajax request for the OBJECT DIALOG
	html = html + '	<script>';
	html = html + '		var url = "/object_dialog/' + url_args + '";';
	html = html + '		$.get(url, function(data) {';
	html = html + '			$("#objectdialog_' + obj_id + '").html(data);';
	html = html + '		});';
	html = html + '	</script>';

	return html;
	
}

function build_no_result(message_override, hide_command_toolbar) {

	if (hide_command_toolbar == true) {
		var control_div = document.getElementById("controls");
		if (control_div !== undefined && control_div !== null) {
			control_div.innerHTML = "";
			control_div.style.visibility = "hidden !important";
			control_div.style.margin = "0px !important";
		}
	}

	var msg = 'There are no results. Please wait at least 1 minute or add objects using the ADD OBJECT function.';
	if (message_override!='') {
		msg = message_override;
	}

	var results = "<div class='alert alert-warning' role='alert'>" + msg + "</div>";
	write_results(results);

}

function write_results(results) {

	var chartDiv = document.getElementById("vis");
	var result_container = "<div style='padding-top:20px;'>" + results + "</div>";

	chartDiv.style.height = "400px"
	chartDiv.innerHTML = result_container;

}

function populate_select_with_objects_via_ajax(elem_id, url, fieldname, fieldvalue, unselected_text, include_model) {

	// retrieve properties per OBJECT
	$.getJSON(url, function(data) {
	
		// get the select object to modify 
		var obj_select = $('#'+elem_id);
		
		// get the objects from the AJAX call		
		objects = data['data'];
				
		var new_options = "<option value=''>" + unselected_text + "</option>";
		
		// iterate through objects and populate values into the select html
		for (var i = 0; i < objects.length; i++){
		    var obj = objects[i];
		    var option_txt = obj[fieldname];
		    if (include_model == true && obj.model_name !== undefined) {
				option_txt = obj.model_name + ": " + option_txt;	    	
		    }
		    
       		new_options = new_options + "<option value='" + obj[fieldvalue] + "'>" + option_txt + "</option>";
		}

		obj_select.html(new_options);
				
	});

}

function _populate_object_select_by_classtype(classtype_key, select_id, select_text) {

	var url = '/api/v1/get_objects_by_model_classtype/' + classtype_key + '/0/0';
	populate_select_with_objects_via_ajax(select_id, url, 'name', 'id', select_text, true);

}

function _populate_object_select_by_subclasstype(subclasstype_key, select_id, select_text) {

	var url = '/api/v1/get_objects_by_model_subclasstype/' + subclasstype_key + '/0/0';
	populate_select_with_objects_via_ajax(select_id, url, 'name', 'id', select_text, true);
		
}

function _display_message(msg_log, msg_ui) {

	console.log(msg_log);
	$('.help-inline.error').html(msg_ui);

}

function _retrieve_objects_by_subclasstype(subclasstype_id, callback_fn) {

	// build url		
	var url = '/api/v1/get_objects_by_subclasstype/' + subclasstype_id + '/0/0';
	
	// retrieve the objects for a subclasstype

	$.getJSON(url, function(data) {
	
		var items = [];
		json_data = data['data'];
		
		// add to items  	
		$.each( json_data, function( key, val ) {
			items.push(val);
		});
		
		// sort the items
		items.sort(function(a, b) {
			return a.name.toLowerCase().localeCompare(b.name.toLowerCase());
		});
		
		// populate
		callback_fn(classtype_id, items);
		
	});

}

function _retrieve_objectmodels_by_subclasstype(classtype_id, callback_fn) {

	// build url		
	var url = '/api/v1/get_objectmodels_by_subclasstype/' + classtype_id + '/0';
	
	// retrieve the models per classtype

	$.getJSON(url, function(data) {
	
		var items = [];
		json_data = data['data'];
		
		// add to items  	
		$.each( json_data, function( key, val ) {
			items.push(val);
		});
		
		// sort the items
		items.sort(function(a, b) {
			return a.description.toLowerCase().localeCompare(b.description.toLowerCase());
		});
		
		// populate
		callback_fn(classtype_id, items);
		
	});

}

function _retrieve_subclasstypes(callback_fn) {

	// Return all the (SUB) classtypes for all OBJECTs registered in the system
	$.getJSON( "/api/v1/get_model_subclasstypes/ALL/1/0", function( data ) {
	
		var items = [];
		var item_description = '';
		var item_id = 0;

	  	json_data = data['data'];
	
		// add to items  	
		$.each( json_data, function( key, val ) {
			item_description = val.value[0]['description'];
			item_id = val.value[0]['value'];
			if (item_description == "" || item_description == "None" || parseInt(item_id)==0 || parseInt(item_id)==999999) {
				// do not add
			} else {
		   		items.push(val);
		   	}
    	});
    	
    	// sort the items
		items.sort(function(a, b) {
   			return a.value[0]['description'].toLowerCase().localeCompare(b.value[0]['description'].toLowerCase());
		});    	

		callback_fn(items);
    			
   	});
   	
}

function _remove_element(element_id) {

	// remove the element 
	var element = document.getElementById(element_id);
	if (element !== undefined) {
		var parent_node = element.parentNode;
		parent_node.removeChild(element);
	}
	
}

function _get_sorted_list_by_name(data) {

	var items = [];

	// add to items list  	
	$.each(data, function( item ) {
		items.push(data[item]);
	});

	// sort the items
	items.sort(function(a, b) {
		return a.name.toLowerCase().localeCompare(b.name.toLowerCase());
	});

	return items;
	
}

function _get_sorted_list(data) {

	var items = [];

	// add to items list  	
	$.each(data, function( item ) {
		items.push(data[item]);
	});

	// sort the items
	items.sort(function(a, b) {
		return a.description.toLowerCase().localeCompare(b.description.toLowerCase());
	});

	return items;
	
}

function _get_grouped_lists(data, sort_field) {

	var groups = {};
	generic_key = "general";
	group_key = null;
	
	for (var key in data){
	
		group_key = '';
		item = data[key];
		
		if (item.ui_group !== undefined) {
			group_key = item.ui_group;
		} else {
			var attributes = item.attributes;
			if (attributes === undefined || attributes == null) {
				// no group key
			} else {
				group_key = attributes[0].ui_group;
			}
		}
		
		if (group_key=='' || group_key=='undefined' || group_key === undefined) {
			group_key = generic_key;
		}
		
		if (!groups[group_key]) {
			groups[group_key] = [];
		}
		
		groups[group_key].push(item);
		
	}
	
	// now sort them
	for (var key in groups){
		if (sort_field=='name') {
			sorted_list = _get_sorted_list_by_name(groups[key]);
		} else {
			sorted_list = _get_sorted_list(groups[key]);
		}
		groups[key] = sorted_list;
	}

	return groups;
	
}