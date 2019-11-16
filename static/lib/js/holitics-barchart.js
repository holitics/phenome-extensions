// holitics-barchart.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project
//
// Multi-bar barchart utilizing the d3 charting library
//
// dependencies:
//	 - JS:  v4 of the d3 charting library (d3.v4.min.js)
// 	 - JS: 	app-specific caller JS file
//	 - CSS: holitics-barchart-1.0.css
//   - tooltips: d3tip-v4.js


// FIRST - define some defaults (changeable by caller)

var legend_icon_size = 19;
var margin = {top: 70, right: 30, bottom: 30, left: 30};
var default_chart_height = 400;
var default_chart_width = 350;
var default_bar_width = 74;

// build a MULTI-BAR VERTICAL BAR CHART
// requires a DIV in the caller page called "vis" to be present

function buildPlot(json, series_data_columns, yaxis_title, bar_colors) {

	// get the keys
  	var keys = series_data_columns;
	// get the data we are interested in
	var json_data = json['data'][0]
	// get results
	var results_data = json_data['results']
	// get descriptions
	var descriptions = json_data['info']['descriptions']
	// take the first in the keys as the data series to walk
	var series = results_data[keys[0]];
	// create indices list - number of bar-subject groups
	var indices = Object.keys(series);


	// define the chart area and get the visible width
	var chartDiv = document.getElementById("vis");
	var chartDivWidth = chartDiv.getBoundingClientRect().width;

	// define the margins, width, and height of the canvas
	var width = chartDivWidth - margin.left - margin.right;
	var height = default_chart_height - margin.top - margin.bottom;

	// if there are a small number of bars on a huge area, minimize size of chart 
	var optimal_width = (indices.length)*(2*100)
	if (width>optimal_width) {
		width = optimal_width;
		if (width < default_chart_width) {
			width = default_chart_width;
		}
	}

	// create the canvas
	svg = d3.select(chartDiv).append("svg");

	// set the attributes of the canvas, including fade-in
	svg = d3.select("svg")
		.attr("class", "fade-in")
		.attr("width", width + margin.left + margin.right)
    	.attr("height", height + margin.top + margin.bottom);
    
    
	// Setup the tool tip
    // See original documentation for more details on styling: http://labratrevenge.com/d3-tip/
    var tool_tip = d3.tip()
    	.attr("class", "d3-tip")
      	.offset([-8, 0])
      	.html(function(d) {
			var tooltip_txt = build_tooltip(results_data, d.key, d.value['id']);
			if (tooltip_txt == null) {
				return null;
			} else { 
				return tooltip_txt;
			}
      	});
    
    // activate the tooltip
    svg.call(tool_tip);
        
    
	// define the area to draw on
	var g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	
	// define the scales/bounds of the axes
	
	// define padding between series groups (x% of total series width)
	var x0 = d3.scaleBand().rangeRound([0, width]).paddingInner(0.2);
	// set the number of vertical bars on the X-axis
    x0.domain(indices.map(function(d) { console.log('x0:' + d); return d; }));
	
	var xLabels = d3.scaleBand().rangeRound([0, width]).paddingInner(0.2);
    xLabels.domain(indices.map(function(d) { console.log('xLabels:' + d); return build_index_labels(json_data, d); }));
	
	// define padding between bars in group (x% of total series width)
	var x1 = d3.scaleBand().padding(0.05);
    // set the width of the vertical bars on the X-axis
	x1.domain(keys).rangeRound([0, x0.bandwidth()]);

	// setup y scale based on height of chart	
	var y = d3.scaleLinear().rangeRound([height*0.8, 0]);
	// set the height of the Y-axis
	y.domain([0, d3.max(indices, function(d) { return d3.max(keys, function(key) { return results_data[key][d];}); })]).nice();

	// define the range of the legend
	var z = d3.scaleOrdinal().range(bar_colors);


	// BUILD THE CHART
	   
	// build the initial plot of bars / data
	// add a set of bars for each index subject "d"
	// each set will contain a bar value for each column in "keys"
		
	g.append("g")
    	.selectAll("g")
    	.data(indices)
    	.enter().append("g")
      	.attr("transform", function(d) { return "translate(" + x0(d) + ",0)"; })
    	.selectAll("rect")
    	.data(function(d) { 
    		return keys.map(
    			function(key) {
    				// console.log(results_data[key] + ":" + results_data[key][d] + ", loc=" + x0(d));
    				return {key: key, value: {id: d, value: results_data[key][d], xloc: x0(d)}};
    			});
    		})
    		.enter().append("rect")
      		.attr("x", function(d) { return x1(d.key); })
      		.attr("y", function(d) { return y(d.value['value']); })
      		.attr("width", x1.bandwidth())
      		.attr("height", function(d) { return height - y(d.value['value']); })
      		.attr("fill", function(d) { return z(d.key); })
			.on("mouseover", tool_tip.show )
      		.on("mouseout", tool_tip.hide );


	// CHART - AXES
	_build_axes(g, height, margin, x0, x1, xLabels, y, yaxis_title);

	// LEGEND
	_build_legend(g, width, legend_icon_size, indices, keys, descriptions, z);

	// TEXT LABELS ON TOP OF BARS
	_add_text_labels(g, results_data, indices, keys, x0, x1, y);
	
	// set the data into a dict and return for caller use, if needed
 	var chart_objs = { 'g': g, 'x0':x0, 'x1':x1, 'y':y, 'z':z, 'data':json['data'][0], 'indices':indices}

	// return objs	
	return chart_objs;

}

function _build_axes(g, height, margin, x0, x1, xLabels, y, yaxis_title) {

	// setup x-axis
	g.append("g")
    	.attr("class", "axis")
      	.attr("transform", "translate(0," + height + ")")
		.attr("class", "axisLight")
     	.call(d3.axisBottom(xLabels));

	// setup y-axis
	g.append("g")
    	.attr("class", "axis")
    	.append("text")
      	.attr("x", -(margin.left-10))
     	.attr("y", y(y.ticks().pop()) - (margin.top-10))
      	.attr("dy", "0.42em")
      	.attr("fill", "#fff")
      	.attr("font-weight", "bold")
      	.attr("text-anchor", "start")
      	.text(yaxis_title);


}

function _add_text_labels(g, data, indices, keys, x0, x1, y) {

	key_len = Object.keys(keys).length

	// TEXT LABELS ON TOP OF BARS
	g.append("g")
		.selectAll("g")
		.data(indices)
		.enter().append("g")
		.attr("transform", function(d) { console.log('d='+d); return "translate(" + x0(d) + ",0)"; })
		.selectAll("text.bar")
		.data(function(d) { return keys.map(function(key) {
				// calls customized add_text_labels function in application specific js
				return add_text_labels(data, key, d);
			}); 
		})
		.enter().append("text")
			.attr("class", function(d) { return d.value['class']})
			.attr("text-anchor", "middle")
			.attr("x", function(d) { return x1(d.key) + (x0.bandwidth()/(key_len*2)) - 5; })
			.attr("y", function(d) { return y(d.value['value']) - 10; })
			.text(function(d) { return d.value['text_label']; });

}

function _build_legend(g, width, icon_size, indices, keys, descriptions, z) {

	// colored squares for legend
	var ls_w = icon_size, ls_h = icon_size;

	// define the legend
	var legend = g.append("g")
		.attr("y", 0)
    	.attr("font-family", "sans-serif")
      	.attr("font-size", 10)
      	.attr("text-anchor", "end")
    	.selectAll("g")
    	.data(keys.slice().reverse())
    		.enter().append("g")
      		.attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

	legend.append("rect")
    	.attr("x", width - ls_w)
		.attr("y", function(d, i) {
    		return (-50);
  		})
      	.attr("width", ls_w)
      	.attr("height", ls_h)
      	.attr("fill", z)
      	.style("opacity", 0.8);

	// text for legend
	legend.append("text")
      	.attr("x", width - 24)
      	.attr("y", function(d, i) {
			return (- 40); //<-- position in group
  		})
    	.attr("dy", "0.32em")
      	.attr("fill", "#fff")
      	.text(function(d) { return descriptions[d]; });


}


// GENERIC ADD TEXT LABELS FUNCTION (FOR OTHER APPS)
// -------------------------------------------------
// DEVS: Move to app specific JS file 
//       rename to: add_text_labels(...)
//       and modify as needed

function add_text_labels_NAME_TBD(json_data, key, d) {

	// first set the original value
	return_value = {"value": json_data[key][d]};
	
	// this is the value that will be shown on the bar
	return_value['text_label'] = json_data[key][d];
	
	// this is the class that will be used to control display properties
	return_value['class'] = 'bar_text';
	
	// return dict to the barchart generation code
	return {key: key, value: return_value}; 

}



