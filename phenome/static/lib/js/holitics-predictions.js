// holitics-predictions.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project
// 
// simple javascript interface to prediction stats

function displayPredictiveModelStats(object_classtype) {

	var url = '/api/v1/get_predictivemodel_stats/' + object_classtype + '/0';
	
	$.getJSON(url, function(json) {
		_display_model_stats(json.data[0]);
	})
	.fail(function() {
		_display_init_alert();
	})
	.done(function() { 
		// do nothing
	 });

}

function _display_init_alert() {
	write_results("<div class='alert alert-info' role='alert'>Model Manager Initializing ... please wait</div>");
}

function _display_model_stats(data) {

	var result = "<table id='infotable' class='infotable text-light'>";

	for (var key in data) {
		// start with 1 minute data
		item = data[key]['ONE_MINUTE'];
		accuracy = item['accuracy'];
		model_state = item['state'];
		err_msg = item['last_error'];
		rmse = item['rmse'];
		last_updated = item['last_update_time'];
		
		if (err_msg === 'undefined') {
			err_msg = '';
		}
		badge_value = 'badge-dark';
		badge_value_accuracy = 'badge-dark';
		
		if (model_state=='TESTING') {
			badge_value = 'badge-primary';
		} else if (model_state=='INITIALIZED') {
			badge_value = 'badge-secondary';
		} else if (model_state=='TRAINING') {
			badge_value = 'badge-info';
		} else if (model_state=='OPTIMIZED') {
			badge_value = 'badge-success';
		} else if (model_state=='WAITING') {
			badge_value = 'badge-warning';
		}
		
		accuracy = accuracy.toFixed(2);
		
		// choose the correct badge for model accuracy
		if (accuracy>=90) {
			badge_value_accuracy = 'badge-success';
		} else if (accuracy>=70) {
			badge_value_accuracy = 'badge-info';
		} else if (accuracy>=50) {
			badge_value_accuracy = 'badge-warning';
		} else {
			badge_value_accuracy = 'badge-danger';
		}

		if (accuracy <= 0) {
			accuracy = '--.--';
		} else {
			accuracy = accuracy + " %";
		}

		if (err_msg.length!=0) {
			if (last_updated !== undefined) {
				err_msg = err_msg + "<BR>Last Updated: " + last_updated;
			}
		}
		
		result = result + "<tr><td>" + key + "</td>";
		result = result + "<td class='stats-badge'>State<h4><span class='badge " + badge_value + "'>" + model_state + "</span></h4></td>";
		result = result + "<td class='stats-badge'>Accuracy<h4><span class='badge " + badge_value_accuracy + "'>" + accuracy + "</span></h4></td>";
		result = result + "<td class='stats-badge'><span>" + err_msg + "</span></td>";

		result = result + "</tr>";
			
	}

	result = result + "</table>";
	
	write_results(result);


}
