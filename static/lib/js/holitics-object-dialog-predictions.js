// holitics-object-dialog-predictions.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project

// Includes all js functions needed for prediction summary and charts

var populate_predictions_summary_data = function(rawData) {

	// this is the result
	var predictions = rawData['data'];
	var summary_content = '';

	if (predictions.length == 0) {
	
		summary_content = "There is no prediction data for this object.";
	
	} else {

		var result = "<table id='infotable' class='infotable text-dark'>";

		predictions.forEach(function(obj) {

			model_id = obj.model_id;
			object_id = obj.object_id;
			metric_id = obj.metric;
			model_data = obj.stats

			result = result + "	<tr>";

			if (typeof obj.current !== 'undefined') {

				p_val = obj.predicted;
				c_val = obj.current;

				badge_value_accuracy = get_badge_accuracy(get_accuracy_from_values(c_val, p_val));

				drilldown_url = "<a href='javascript:setup_predictions_chart_div(" + object_id + ",\"" + metric_id + "\");'><img src='/static/images/chart_1.png'></a>";

				result = result + "		<td class='stats-badge'>Metric<h4><span class='badge'>" + metric_id + "</span></h4></td>";
				result = result + "		<td class='stats-badge'>Current<h4><span class='badge'>" + c_val.toFixed(2) + "</span></h4></td>";
				result = result + "		<td class='stats-badge'>Predicted<h4><span class='badge " + badge_value_accuracy + "'>" + p_val.toFixed(2) + "</span></h4></td>";
				result = result + "		<td>" + drilldown_url + "</td>";

			} else {

				result = result + _build_predictive_model_stats_row_contents(metric_id, model_data, false);

			}

			result = result + "	</tr>";

		});

		summary_content = result + "</table>";
		
	}

	_launch_modal_dialog("Predictions", "prediction_summary", summary_content, null, clicked_summary_ok, false);

}


var populate_predictions_chart_data = function(chartTitle, rawData) {

	var predictions = rawData['data'];

	_launch_modal_chart("Prediction Chart - " + chartTitle, "chart_dialog",
		"", null, clicked_chart_ok, true);

	var parseTimestamp  = d3.time.format("%s").parse;
	var data = [];
	var v1 = 0;
	var v2 = 0;
	var ts = 0;
	var vdate = '';
	var vdatenow = new Date(Date.now());

	predictions.forEach(function(obj) {

		v1 = obj.current;
		v2 = obj.predicted;
		vdate = new Date(obj.timestamp); // parseTimestamp(ts);

		// take the last datapoint with both a current and predicted measurement, and call that "now"
		if (v2 !== 'undefined' && v1 !== 'undefined') {
			vdatenow = vdate;
		}

		data.push({
		  date:  vdate,
		  value1: v1,
		  value2: v2
		});

		// console.log('predicted:' + obj.predicted + ", current:" + obj.current + ", vdate:" + vdate);

	});

	var markers = [
		{
			"date": vdatenow,
			"type": "Now",
			"caption": ""
		}
	];

	makeChart(data, markers, "modal-chart-body", "Current", "Predicted");
	
}

function clicked_chart_ok() {

	// remove the modal chart
	$('#centered_modal_chart').modal('hide');

}


function clicked_summary_ok() {

	// remove the modal summary
	$('#centered_modal_dialog').modal('hide');

}