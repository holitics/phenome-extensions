// holitics-predictions.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project
// 
// simple javascript interface to prediction stats

function displayPredictiveModelStats(object_classtype) {

	var url = '/api/v1/get_predictivemodel_stats/' + object_classtype + '/0';
	
	$.getJSON(url, function(json) {
		_display_predictive_model_stats(json.data[0]);
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

function _build_predictive_model_stats_row_contents(key, item, include_error_msg) {

	result = "";

	if (typeof item === 'undefined') {

		accuracy = 0.0;
		model_state = 'INITIALIZED';
		err_msg = '';
		badge_value = 'badge-dark';
		badge_value_accuracy = 'badge-dark';

	} else {

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

		if (model_state == 'TESTING') {
			badge_value = 'badge-primary';
		} else if (model_state == 'INITIALIZED') {
			badge_value = 'badge-secondary';
		} else if (model_state == 'TRAINING') {
			badge_value = 'badge-info';
		} else if (model_state == 'OPTIMIZED') {
			badge_value = 'badge-success';
		} else if (model_state == 'WAITING') {
			badge_value = 'badge-warning';
		}

		accuracy = accuracy.toFixed(2);

		// choose the correct badge for model accuracy
		badge_value_accuracy = get_badge_accuracy(accuracy);

	}

	if (accuracy <= 0) {
		accuracy = '--.--';
	} else {
		accuracy = accuracy + " %";
	}

	result = result + "		<td class='stats-badge'>Model<h4><span class='badge'>" + key + "</span></h4></td>";
	result = result + "		<td class='stats-badge'>State<h4><span class='badge " + badge_value + "'>" + model_state + "</span></h4></td>";
	result = result + "		<td class='stats-badge'>Accuracy<h4><span class='badge " + badge_value_accuracy + "'>" + accuracy + "</span></h4></td>";

	if (err_msg.length!=0 && include_error_msg) {
		if (last_updated !== undefined && last_updated > 0) {
			err_msg = err_msg + "<BR>Last Updated: " + get_current_time_from_unix_timestamp(last_updated/1000);
		}
		result = result + "		<td class='stats-badge'><span>" + err_msg + "</span></td>";
	}

	return result;

}

function get_accuracy_from_values(value1, value2) {

	if (value1 < value2) {
		return ((value1 / value2) * 100);
	} else {
		return ((value2 / value1) * 100);
	}

}

function get_badge_accuracy(accuracy) {

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

	return badge_value_accuracy;

}

function _display_predictive_model_stats(data) {

	var result = "<table id='infotable' class='infotable text-light'>";

	for (var key in data) {
		result = result + "	<tr>";
		item = data[key]['ONE_MINUTE']
		result = result + _build_predictive_model_stats_row_contents(key, item, true);
		result = result + "	</tr>";
	}

	result = result + "</table>";
	
	write_results(result);

}

function get_current_time_from_unix_timestamp(timestamp){

  var a = new Date(timestamp * 1000);
  var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var year = a.getFullYear();
  var month = months[a.getMonth()];
  var date = a.getDate();
  var hour = a.getHours();
  var min = a.getMinutes();
  var sec = a.getSeconds();
  var time = date + ' ' + month + ' ' + year + ' ' + timepad(hour) + ':' + timepad(min) + ':' + timepad(sec) ;

  return time;

}

function timepad(num) {
  return ("0"+num).slice(-2)
}

