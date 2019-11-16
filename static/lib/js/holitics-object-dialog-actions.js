// holitics-object-dialog-actions.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project

// Includes all js functions needed for object actions dialog.

var populate_actions = function(obj_id, data) {

	// this is a dictionary
	actions = data['data'][0]['actions'];

	var action_items = _get_sorted_list(actions);
	var ui_models = data['data'][0]['ui_models'];
	var enum_values = data['data'][0]['enum_values'];
	var state_values = data['data'][0]['state_values'];
	var buttons_added = {};
	var obj_action_div_id = '#obj_actions_' + obj_id;
	var content = '';
	
	// empty the DIV
	$(obj_action_div_id).empty();

	// get a grouped, sorted dictionary of lists of actions
	groups = _get_grouped_lists(action_items,'description');
	
	for (var key in groups) {

		content = content + "<h6 class='dropdown-header'><center>-- " + key + " actions --</center></h6>";
	
		// populate all the actions for this group
		content = content + _populate_actions(obj_id, data, groups[key], ui_models, enum_values, state_values, obj_action_div_id, buttons_added);
		
	}

	hide_loading_spinner();

	_launch_modal_dialog("Actions", "action_dialog", content, null, null, false);


} // end

function _populate_actions(obj_id, data, action_items, ui_models, enum_values, state_values, obj_action_div_id, buttons_added) {

	var action_content = '';

	action_items.forEach(function(item,index) {
	
		var show_in_ui = item.show_in_ui;

		if (show_in_ui === undefined || show_in_ui == "false") {
		
			// do not show this action
		
		} else {
		
			var has_added = false;
			var button_key = item.id;

			if (item.alter_state !== undefined && item.ui_model !== undefined ) {
				button_key = item.alter_state + "." + item.ui_model;
			}

			has_added = buttons_added[button_key];
			
			if (has_added == false || has_added === undefined) {
			
				var menu_items;

				try {				
					menu_items = _build_ui_action(item, obj_id, ui_models, enum_values, state_values);
				} catch(err) {
					console.log("ERROR (" + err + ") while building action (" + item.id + ")");
				}
			
				if (menu_items !== undefined) {

					// set it into the lookup dict			
					buttons_added[button_key] = button_key;

					var item_count = menu_items.length;
					for (var idx = 0; idx < item_count; idx++) {
						// create the menu item
						menu_item = "<div style='padding-bottom:8px;text-align:center;'>" + menu_items[idx] + "</div>";
						// add the 'button'
						action_content = action_content + menu_item;
					}

				}
				
			}
		
		}
		
	});	// end for each for data

	return action_content;

}

function show_loading_spinner() {

	$("#loading_spinner").show();
	$(".modal-body").css('opacity','0.3');
	$(".modal-body").css('pointer-events','none');

}

function hide_loading_spinner() {

	$("#loading_spinner").hide();
	$(".modal-body").css('opacity','1');
	$(".modal-body").css('pointer-events','auto');

}

function execute_action(action_id, obj_id) {

	// build url		
	var url = '/api/v1/execute_action_by_object/' + obj_id + '/' + action_id + '/0';

	show_loading_spinner();

	$.getJSON(url, function(data) {
		
		// this is the result
		result = data['data'][0]['result'];

		if (result==false) {

			alert("Call to API failed.");

			hide_loading_spinner();

		} else {

			// alert('action_id=' + action_id + ", result=" + result);

			// some built in actions to the current UI
			if (action_id == 'delete' && result == true) {
				location.reload();
			}
		
			// refresh the object dialog again, just in case
			refresh_object_dialog(obj_id);

			// now launch the actions buttons again
			setup_actions_div(obj_id);

		}

	});

}

function _replace_keyword_values(item_with_keyword, values) {

	if (item_with_keyword=='' || item_with_keyword === undefined) {
		return '';
	}

	new_item = item_with_keyword;

	if (item_with_keyword.indexOf("{")>=0) {
		i0 = item_with_keyword.indexOf("{");
		i1 = item_with_keyword.indexOf("}");
		kw = item_with_keyword.substring(i0+1,i1);
		kw_value = values[kw];
		new_item = item_with_keyword.substring(0,i0) + kw_value + item_with_keyword.substring(i1+1,item_with_keyword.length);
	}

	return new_item;

}

function _build_button_title(item, model) {

	var button_title = '';

	if (model !== undefined) {
		button_title = model['title'];
	}

	if (item.ui_button_title !== undefined) {
		// if there is a specific UI title specified for this button, USE IT
		button_title = item.ui_button_title;
	}

	if (button_title == "" || button_title === undefined) {
		if (item.description !== undefined) {
			button_title = item.description;
		} else {
			button_title = 'EXECUTE';
		}
	}

	return button_title;

}

function _build_ui_action(item, obj_id, ui_models, enum_values, state_values) {

	var ui_model = item.ui_model;
	var model = ui_models[ui_model];
	var menu_items = [];
	var menu_item = null;
	var button_type = null;
	var button_style = '';

	if (model !== undefined) {

		// deal with all model stuff here EXCEPT button titles
		button_type = model['type'];
		button_style = model['style'];

		if (button_style=="" || button_style===undefined) {
			button_style='light';
		}

	}

	// Here, we build the overall button title for the button
	// if there are multiple buttons to be built here, they will
	// usually come as a STATE DICTIONARY and include a name/title
	// for each button

	var button_title = _build_button_title(item, model);

	if (ui_model === undefined || ui_model == "generic_button") {

		if (button_title == item.description) {
			// let's not be too repetitive
			button_title = 'EXECUTE';
		}

		menu_item = "<div style='width:75%;text-align:left;position: absolute;'>" + item.description + "</div>";
		menu_item = menu_item + "<div style='text-align:right;'>";
		menu_item = menu_item + "<button type='button' class='btn btn-sm btn-primary action-button' " + _build_action_click_html(item.id, obj_id) + ">" + button_title + "</button>";
		menu_item = menu_item + "</div>";

		// make it look like a button
// 		menu_item = "<a class='btn btn-object-action btn-primary btn-sm ' role='button' href='#' " + _build_action_click_html(item.id, obj_id) + ">" + item.description + "</a>";
		menu_items.push(menu_item);
			
	} else if (ui_model.startsWith('confirm_button_')) {
			
		// so the CONFIRM part will load a MODAL

		menu_item = "<div style='width:75%;text-align:left;position: absolute;'>" + item.description + "</div>";
		menu_item = menu_item + "<div style='text-align:right;'>";
		menu_item = menu_item + "<button type='button' class='btn btn-sm btn-" + button_style + " action-button' " + _build_modal_action_click_html(item.id, obj_id, item) + ">" + button_title + "</button>";
		menu_item = menu_item + "</div>";

		menu_items.push(menu_item);

	} else {

		var alter_state = item.alter_state;
		var state_value_items = [];
		
		if (alter_state !== undefined && state_values !== undefined) {
			current_state = state_values[alter_state];
			if (Array.isArray(current_state)) {
				state_value_items = current_state;
			} else {
				state_value_items[0] = current_state;
			}
		}

		// look up ui_model info for this button
		//button_type = model['type'];
		//button_title = model['title'];

		if (item.state_enum !== undefined) {
			enum_state_values = enum_values[item.state_enum];
		}

		var item_count = state_value_items.length;

		for (var idx = 0; idx < item_count; idx++) {

			state_value_item = state_value_items[idx];

			if(state_value_item == null) {
  				// null or undefined
			} else if (typeof state_value_item == "object") {
				// assume we are using a state info dictionary
				current_state = state_value_item.state;
				current_name = state_value_item.name;
				if (state_value_item.name !== undefined) {
					button_title = state_value_item.name
				}

			} else {
				current_state = state_value_item;
			}

			current_state = current_state.toString();

			if (button_type == 'toggle_button') {

				data_onstyle = model['data-onstyle'];
				data_offstyle = model['data-offstyle'];

				data_on = model['data-on'];
				data_off = model['data-off'];

				data_on_caption = model['data-on-caption'];
				data_off_caption = model['data-off-caption'];

				data_on_caption_pressed = model['data-on-caption-pressed'];
				data_off_caption_pressed = model['data-off-caption-pressed'];

				if (data_on_caption === undefined) {
					data_on_caption = data_on;
				}

				if (data_off_caption === undefined) {
					data_off_caption = data_off;
				}

				if (data_on_caption_pressed === undefined) {
					data_on_caption_pressed = data_on_caption;
				}

				if (data_off_caption_pressed === undefined) {
					data_off_caption_pressed = data_off_caption;
				}

				action_on = _replace_keyword_values(model['action-on'], state_value_item);
				action_off = _replace_keyword_values(model['action-off'], state_value_item);
				button_title = _replace_keyword_values(button_title, state_value_item);

				on_disabled = "";
				off_disabled = "";

				pressed = "aria-pressed='true'";
				on_pressed = pressed;
				off_pressed = pressed;

				// first, look at the current state
				data_on_state = enum_state_values[data_on]
				data_off_state = enum_state_values[data_off]
				alter_disabled_style = model['alter-disabled-style']

				if (alter_disabled_style === undefined) {
					alter_disabled_style = false;
				}

				// convert to strings, sometimes these things are bool, ints, strings, etc.
				data_on_state = data_on_state.toString();
				data_off_state = data_off_state.toString();

				if (current_state.toLowerCase() == 'true' || current_state.toLowerCase() == 'false') {
					// ok if they are supposed to be bools, convert to bools so testing is easy
					current_state = (current_state.toLowerCase() == "true");
					data_on_state = (data_on_state.toLowerCase() == "true");
				}

				if (data_on_state === current_state) {

					// it's ON, so ON should be disabled
					//alert('on (2nd button) will be disabled');
					on_disabled = "disabled";

					if (alter_disabled_style) {
						data_offstyle = "outline-secondary";
					}

					off_pressed = "";
					data_on_caption = data_on_caption_pressed;

					// we want to see the ON color, the OFF color can be muted
					on_style_override = "opacity:1;"
					off_style_override = "opacity:1;"

				} else {

					//alert('off (1st button) will be disabled');
					off_disabled = "disabled";
					if (alter_disabled_style) {
						data_onstyle = "outline-secondary";
					}
					on_pressed = "";
					data_off_caption = data_off_caption_pressed;

					// we want to see the OFF color, the ON color can be muted
					off_style_override = "opacity:1;"
					on_style_override = "opacity:1;"

				}

				if (current_state == 'DISABLED' || current_state == 'UNKNOWN' || current_state == 'CYCLE') {
					off_disabled = "disabled";
					on_disabled = "disabled";
				}

				button_group = "<div style='width:75%;text-align:left;position: absolute;'>" + button_title + "</div>";
				button_group = button_group + "<div class='btn-group btn-object-action' role='group' aria-label='" + item.id + "' style='text-align:right;display:block;'>";
				button_group = button_group + "<button type='button' style='" + off_style_override + "' class='btn btn-sm btn-" + data_offstyle + "' " + off_disabled + " " + off_pressed + " " + _build_action_click_html(action_off, obj_id) + ">" + data_off_caption + "</button>";
				button_group = button_group + "<button type='button' style='" + on_style_override + "' class='btn btn-sm btn-" + data_onstyle + "' " + on_disabled + " " + on_pressed + " " + _build_action_click_html(action_on, obj_id) + ">" + data_on_caption + "</button>";
				button_group = button_group + "</div>";

				menu_item = button_group;

			} // end toggle type

			// add to the array
			menu_items.push(menu_item);

		} // end iterate over state_items

	}

	return menu_items;

}


function _build_action_click_html(action_id, object_id) {

	var onclick = "onclick='javascript:execute_action(" + "\"" + action_id + "\"" + "," + object_id + ");'"
	return onclick;

}

function _build_modal_action_click_html(action_id, object_id, item) {

	// create options to store in the local dict
	var settings = {
		"action": action_id,
		"object": object_id,
		"title": item.description,
		"confirm": item.ui_confirmation
	}

	// store them
	modal_settings[action_id] = settings;

	// create the click component
	var onclick = "onclick='javascript:_launch_modal_action_confirm_dialog(" + "\"" + action_id + "\"" + ");'"
	return onclick;

}

function clicked_modal_confirm_action_button() {

	action_id = last_modal_id;
	object_id = modal_settings[action_id]['object'];
	
	// remove the modal dialog
	$('#centered_modal_dialog').modal('hide');

	execute_action(action_id, object_id);

}

function _launch_modal_action_confirm_dialog(action_id) {

	var title = modal_settings[action_id]['title'];
	var confirm_txt = modal_settings[action_id]['confirm'];
	
	var modal = $('#centered_modal_dialog');
	var modal_button_dismiss = $('#centered_modal_dialog_button_dismiss');
	var modal_button = $('#centered_modal_dialog_button_confirm');
	
	// set the title and text
	modal.find('.modal-title').text(title);
	modal.find('.modal-body').html(confirm_txt);
	
	modal_button.text('GO FOR IT!');
	modal_button.click(clicked_modal_confirm_action_button);
	
	modal_button_dismiss.hide();
	modal_button.show();
	
	
	// set the last modal id (ugly!) so it can be retrieved by the click!
	last_modal_id = action_id;
		
	// show the modal
	$('#centered_modal_dialog').modal('show');
	
}