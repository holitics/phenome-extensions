// holitics-dialog-addobject.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project

var models = [];
var classtypes = [];

function clicked_classtype_id(classtype_id) {

	// clear all OTHER classtypes
	for (i = 0; i < classtypes.length; i++) {
		if (classtypes[i]!=classtype_id) {
			$('#classtype_' + classtypes[i]).empty();
		}
	}
}

function clicked_model_id(classtype_id, model_id) {
 
	// clear all OTHER models
	for (i = 0; i < models.length; i++) {
		if (models[i]!=model_id) {
			$('#model_' + models[i]).empty();
		}
	}

	// now build the add/EDIT panel	
	display_required_properties_by_model(model_id);

}

function _clean_description(item_description) {

	var i = item_description.indexOf(" of the ");
	if (i==-1) {
		i = item_description.indexOf(" to ");
	}
	
	if (i>1) {
		item_description = item_description.substring(0, i);
	}

	return item_description;

}

function display_required_properties_by_model(model_id) {

	// clear the attributes/properties of this model id, if applicable
	$('#model-attributes-' + model_id).empty();

	var populate_parameters = function(data) {

		// add a nice line
		$('#model-attributes-' + model_id).append('<div><HR></div>');
	
		// start the add panel
		var add_panel = '' + 
				'<div class="panel panel-default" id="add_model_attributes_panel">'+
				  '<div class="panel-heading" role="tab" id="add_model_attributes_panel_heading">'+
					'<form id="add-object" class="add-object needs-validation" method="GET" action="/api/v1/add_object_request" novalidate>';

		data.forEach(function(item,index) {

			var item_description = item.description;
			var item_name = item.name;
			var item_key = item.id;
			var item_value = item.value;
			var item_default = item.default_value;
			var item_units = ''; 
			var field_required = '';

			var attributes = null;
			if (item.attributes !=undefined) {
		
				// get the attrs
				attributes = JSON.parse(item.attributes.replace(/'/g,"\""))[0];
			
				// get the units
				item_units = attributes.units;
			
				// is the field required?
				if (attributes.required != undefined && attributes.required == 1) {
					field_required = 'required';
				}
			
			}

			// clean up descriptions
			item_description = _clean_description(item_description);
		
			if (item_value == null) {
				if (item_default != null) {
					item_value = item_default;
				} else {		
					item_value = '';
				}
			}

			// type of field
			var field_type = 'type="text"'
		
			// build the field str			
			var input_form_field_str = '<input ' + field_type + ' data-units="' + item_units + '" style="padding-left:5px;" class="form-control" name="' + item_name + '" id="' + item_name + '" value="' + item_value + '" ' + field_required + '>';

			// build the add panel str
			add_panel = add_panel + 
					'<div class="form-row">'+
						'<div class="col">' +
							'<label style="padding-top:5px;" for="' + item_name + '">' + item_description + '</label>'+
						'</div>'+
						'<div class="col">' +
							input_form_field_str +
							'<div id="feedback-' + item_name + '" class="invalid-feedback">Valid ' + item_description + ' is required.</div>' +
						'</div>'+
					'</div>';

		});	// end for each for data

		// add hidden fields
		add_panel = add_panel + '<input type="hidden" name="_model_id" id="_model_id" value="' + model_id + '">';
	
		// start the end of the add panel
		add_panel = add_panel + 
					'<BR><div class="modal-footer" id="form-footer">'+
						'<button class="btn btn-primary btn-lg btn-block" id="submit" type="submit">Add</button>'+
					'</div>'+
					'<center><span class="help-inline error"></span></center>'+
				'</form>'+
			  '</div>'+
			'</div>';


		$('#model-attributes-' + model_id).append(add_panel);

		attach_ajax_submit_listener('add-object', do_submit_callback_success, do_submit_callback_error);

	}; // end

	// build url		
	var url = '/api/v1/get_required_properties_by_objectmodel/' + model_id + '/0';

	// retrieve the required params per model
	$.getJSON(url, function(data) {

		// alert('got get_required_properties_by_objectmodel');
	
		// empty array
		var items = [];

		var properties = data['data'];
	
		// add to items  	
		$.each( properties, function(key, value) {
			items.push(value);
		});

		// populate
		populate_parameters(items);

	});

				
}

function add_object(object_type) {

	// remove the contents of classtypes
	$('.classtypes').empty();

	// clear the arrays
	classtypes = [];
	models = [];

	var classtype_data = {};

	// a function that populates the classtypes into an accordian panel
	
	var populate_classtypes = function(data) {
	
		data.forEach(function(item,index) {
			
		  	var classtype_id = item.value[0]['value'];
		  	var item_description = item.value[0]['description'];
		  	var item_key = item.id;

			// add to the array of classtypes
			classtypes.push(classtype_id);

		  	var icon = item.value[0]['icon'];
		  	if (icon==undefined) {
		  		icon = '/images/phenome_icon.png';
		  	}
		  	icon = get_image_url(icon);
	  		var icon_str = '<img src="'+icon+'" class="subclasstype_icons">';

			var allow_add = item.value[0]['add_dialog']
			if (allow_add==undefined || allow_add=='true') {
				allow_add = true
			} else {
				allow_add = false
			}
			
			//alert(item_description + ", " + allow_add);
		  	
		  	if (allow_add) {
				$('.classtypes').append(
					'<div class="panel panel-default" id="classtype_'+classtype_id+'">'+
					  '<div class="panel-heading" role="tab" id="heading_'+classtype_id+'">'+
						'<h4 class="panel-title">'+
							icon_str+
							'<a style="padding-left:5px;" role="button" data-toggle="collapse" data-parent="#accordion" href="#collapse_'+classtype_id+'" aria-expanded="true" aria-controls="collapse_'+classtype_id+'">'+
							item_description+
							'</a>'+
						'</h4>'+
					  '</div>'+
					  '<div id="collapse_'+classtype_id+'" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="heading_'+classtype_id+'">'+
							'<div class="panel-body">'+
								'<div id="models_'+classtype_id+'"></div>' +
							'</div>'+
					  '</div>'+
					'</div>'
				); // end append classtypes
			} // end allow_add			
			
			
		});	// end for each for data
	} // end
		
	var populate_modeltypes = function(classtype_id, data) {
	
		$('#models_' + classtype_id).empty();
		
		var count = 0;
		
		data.forEach(function(item,index) {
		
			if (item.description.lastIndexOf("All ")==0) {
				return;
			}
		
		  	var model_id = item.id;
		  	count = count + 1;
		  	
			// add to the array of models
			models.push(model_id);
		
			// build the javascript click URL
			var js_click = "javascript:clicked_model_id("+classtype_id+","+model_id+");";
		
			$('#models_' + classtype_id).append(
				'<div class="panel panel-default" id="model_'+model_id+'">'+
				  '<div class="panel-heading" role="tab" id="heading_'+model_id+'">'+
					'<h6 class="panel-title">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+
						'<a class="add-model-link" role="button" data-target="model_'+model_id+'" id="target_model_'+model_id+'" data-toggle="collapse" data-parent="#accordion" href="' + js_click + '" onclick="' + js_click + '" aria-expanded="true" aria-controls="model_'+model_id+'">'+
						item.description+
						'</a>'+
					'</h6>'+
				  '</div>'+
				  '<div id="panel-attributes-'+model_id+'" class="" role="tabpanel" aria-labelledby="attributes_'+model_id+'">'+
						'<div class="panel-body">'+
							'<div id="model-attributes-'+model_id+'"></div>' +
						'</div>'+
				  '</div>'+
				'</div>'
			); // end append models
				
		
		});	// end for each for data
	
		if (count==0) {
			$('#models_' + classtype_id).append('<div class="panel panel-default" style="margin-top:30px;"><div class="alert alert-info" role="alert" style="margin-bottom:0px !important;"><center>There are no models defined!</center></div></div>');
		}
	
	
	} // end
	
		
	// code to handle the retrieval of models per classtype when the accordian is clicked
	$('#accordion').on('show.bs.collapse', function(e){
	
		// get the classtype
		var classtype_id  = $(e.target).attr('id').replace('collapse_','');

		// remove all other classtypes
		clicked_classtype_id(classtype_id);

		// get the models for this subclasstype
		_retrieve_objectmodels_by_subclasstype(classtype_id, populate_modeltypes);
		
			
	});

	_retrieve_subclasstypes(populate_classtypes);

	// show the Model Dialog
	$('#addModal').modal('show');
			
}

