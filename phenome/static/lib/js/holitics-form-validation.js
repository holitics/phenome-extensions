// holitics-form-validation.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project
//
// some ajax validation methods

<!-- attach submit handler and form validation -->

function attach_ajax_submit_listener(form_id, fn_callback_success, fn_callback_error) {

	// AJAX bootstrap script
	$("button#submit").unbind('click').click(function(){

		var form = $('#'+form_id); // $('form.'+form_id);
		
		// check to see if the form is valid
		is_valid = _validate_form(form);
		
		if (is_valid == false) {
			return false;
		}

		// form must be valid, now submit
		$("button#submit").button('loading');
		$.ajax({
		  url: form.attr('action'),
		  type: form.attr('method'),
		  dataType: 'json',
		  data: form.serialize(),
		  success: function(data, text, xhr){
			$("button#submit").button('reset');
			fn_callback_success(data, text, xhr);
		  },
		  error:function(data, text, error){
			$("button#submit").button('reset');
			fn_callback_error(data, text, error);
		  }
		});
		return false;
			
	});

}

function _validate_website(value) {

	var webRegex = /(http|ftp|https):\/\/[\w-]+(\.[\w-]+)+([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])?/;
	return webRegex.test(value);

}

function _validate_email(value) {

	var emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
	return emailRegex.test(value);

}

function _validate_macaddress(value) {

	var macRegex = /^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$/;
	return macRegex.test(value);

}

function _validate_ipaddress(value) {

	var ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
        ipv6Regex = /^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$/,
        valid     = false,
        message = 'Please enter a valid IP address';

		valid = ipv4Regex.test(value);
		if (valid==false) {
			valid = ipv6Regex.test(value);
		}
	
	return valid;

}

function _validate_form(form_obj) {

	if (form_obj.elements === undefined) {
		form = form_obj[0];
	} else {
		form = form_obj;
	}

	var form_fields = form.elements;
	var error_free=true;
	
	for (var i = 0, element; element = form_fields[i++];) {
	
		required = element.required;

		// units is a custom field
		field_units = element.dataset.units;
		value = element.value;
		valid = true;

		var feedback_element = $("#feedback-" + element.id);
		var error_message = '';
		var tested = false;

		if (required!=undefined && required == true && value != '' && value != undefined) {
		
			// TODO - add custom validation per units type
		
			if (field_units == 'ipaddress') {
				tested = true;
				valid = _validate_ipaddress(value);
				if (valid == false) {
					error_message = "Poor format, for IPv4 use: A.B.C.D";
				}
			}
			
			if (field_units == 'macaddress') {
				tested = true;
				valid = _validate_macaddress(value);
				if (valid == false) {
					error_message = "Poor format, use: AA:BB:CC:DD:...";
				}
			
			}
			
			// TODO - improve control of success/fail of the validations
			// Tried using class names and (classList.add) but it is not working??
			
			if (valid == false) {

				error_free = false;
				feedback_element[0].innerText = error_message;
				feedback_element[0].style.display = "block";
				element.style.borderColor = "#dc3545"; 
				element.focus();

			} else if (tested == true) {
			
				feedback_element[0].style.display = "none";
				element.style.borderColor = "#28a745"; 

			}
			
			
		} // end required check
		
	}

	if (form.checkValidity() === false || error_free == false) {
		event.preventDefault();
		event.stopPropagation();
		error_free = false;
	}
  
	form.classList.add('was-validated');
		
	return error_free == true;

}

<!-- SETUP THE VALIDATION OF FORM -->

function setup_validation() {

	  // Fetch all the forms we want to apply custom Bootstrap validation styles to
	  var forms = document.getElementsByClassName('needs-validation');

	  // Loop over them and prevent submission
	  var validation = Array.prototype.filter.call(forms, function(form) {
	  
		form.addEventListener("submit", function(event) {
		
			_validate_form(form);
		  	
		}, false);
		
	  });
	  
}



    
    