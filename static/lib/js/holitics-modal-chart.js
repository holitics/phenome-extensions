// holitics-modal-chart.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project
//
// Modal chart wrapper functions for Holitics API

var modal_settings = {};
var last_modal_id = null;

function _launch_modal_chart(title, modal_id, content, button_text, button_click, hide_footer) {
	
	var modal = $('#centered_modal_chart');
	var modal_button = $('#centered_modal_chart_button_confirm');
	var modal_button_dismiss = $('#centered_modal_chart_button_dismiss');

	// show the modal footer	
	modal.find('.modal-footer').show();
	
	// set the title and text
	modal.find('.modal-title').text(title);
	
	if (content !== null) {
		modal.find('.modal-chart-body').html(content);
	}
	
	modal.find('.modal-chart').maxWidth='80%';
	modal.find('.modal-chart').maxHeight='80%';
	
	if (button_text !== null && button_text !== undefined) {
		modal_button.text(button_text);
		modal_button.show();
		modal_button_dismiss.text('Cancel');
	} else {
		modal_button.hide();
		modal_button_dismiss.text('OK');
	}
	
	if (button_click !== null) {
		modal_button.click(button_click);
	}
	
	if (hide_footer == true) {
		// hide the modal footer	
		modal.find('.modal-footer').hide();
	} else {
		modal.find('.modal-footer').show();
	}
	
	// set the last modal id (ugly!) so it can be retrieved by the click!
	last_modal_id = modal_id;

	// show the modal
	$('#centered_modal_chart').modal('show');
	
}
