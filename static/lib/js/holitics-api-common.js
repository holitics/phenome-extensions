// holitics-api-common.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project
//
// Common API functions for Holitics API



// build_index_labels
// -------------------
// Method to build an index label from a JSON response
// Takes JSON_DATA and D (the index into the data row)
// D can be a single index (e.g. '1') or a multi-index tuple (e.g. [1,5])

function build_index_labels(json_data, d) {

	// get the index values defined in the info section of the response
	index = json_data['info']['index']

	if (index == undefined) {
		return ""
	}

	label = "";
	index_label = "";
	
	// walk the index	
	var index_length = index.length;
	for (var i = 0; i < index_length; i++) {

		// is it a multi-index ?		
		if (d.indexOf(",") !== -1) {
			x = d.slice(1, -1).split(',')[i];
		} else {
			x = d;
		}

		// get the representative key data
		key_data = json_data['keys'][index[i]][x];
		
		if (index[i]=='object_id') {
			label = key_data['name'];
		} else {
			if (key_data.constructor === Array) {
				label = key_data[0];
			} else {
				label = key_data;
			}
		}
		
		if (index_label == "") {
			index_label = label;
		} else {
			index_label = index_label + " : " + label;
		}

	}
	
	return index_label;	
	
}
