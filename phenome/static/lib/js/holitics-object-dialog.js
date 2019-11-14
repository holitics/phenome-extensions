// holitics-object-dialog.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project

// Includes some basic functions and those needed to launch other dialogs

var _relation_types = null;
var _relation_types_rev = null;

function collapse_toggles(obj_id) {

 	jQuery('.collapse').collapse('hide');
    $('#obj_properties_' + obj_id).empty();
    $('#obj_relations_' + obj_id).empty();
    $('#obj_actions_' + obj_id).empty();

}

function object_dialog_toggle(obj_id, button_id) {
	
	// first collapse/empty the toggles
	collapse_toggles(obj_id);
	
	// launch appropriate button click action
	if (button_id == 1) {
		setup_properties_div(obj_id);
	} else if (button_id == 2) {
		setup_relations_div(obj_id);
	} else if (button_id == 3) {
		setup_actions_div(obj_id);
	}
	
}

function setup_properties_div(obj_id) {

	// build url		
	var url = '/api/v1/get_object_properties/' + obj_id + '/1/0';

	// retrieve properties per OBJECT
	$.getJSON(url, function(data) {
		populate_properties(obj_id, data);
	});
	
}

function setup_actions_div(obj_id) {

	// build url		
	var url = '/api/v1/get_actions_by_object/' + obj_id + '/0';
	
	// retrieve actions per OBJECT
	$.getJSON(url, function(data) {
		populate_actions(obj_id, data);
	});

}

function setup_relations_div(obj_id) {

	populate_relations(obj_id);

}

function refresh_object_dialog(obj_id) {

	// build the arguments for the /object_dialog/ API call
	var url_args = obj_id + '/' + object_dialog_header_only + '/' + object_dialog_show_details;
	var url = "/object_dialog/" + url_args;
	$.get(url, function(data) {
		var obj_dialog_id = "#objectdialog_" + obj_id;
		$(obj_dialog_id).html(data);
	});

}

function _launch_object_dialog_modal(object_id, name) {

	// build the dialog title
	title = name + " [id=" + object_id + "]";
	content = build_object_dialog(object_id);
	_launch_modal_dialog(title, "object_dialog", content, null, null, true);

}

function _refresh_object_dialog(object_id) {

	content = build_object_dialog(object_id);

}


function draw_canvas_icons(power_state, object_id) {

	var c = document.getElementById("object_dialog_header_canvas_" + object_id);
	var ctx = c.getContext("2d");
	var fill_color = "#9e9e9e";
	
	if (power_state == 1) {
		fill_color = "#ff0000";
	} else if (power_state == 2) {
		fill_color = "#77ff00";
	}
	
	ctx.fillStyle = fill_color;
	canvas_x = c.width - (c.width*0.05) - 15;
	ctx.fillRect(canvas_x, 5, 10, 10);

}

	
	   		
	