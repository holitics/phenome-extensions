// holitics-diffchart.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project

// Based on the d3 library.
// Will display a time-series chart of a main series of data 
// and another series in comparison (and paint area in between)

// There is a CSS file associated with this js file

var transition_delay = 300;
var legendWidth = 175;
var legendHeight = 40;
var chartHeight = 0;

var numtimes = 0;

function addAxesAndLegend (svg, xAxis, yAxis, margin, chartWidth, chartHeight, title1, title2) {

  var legendStartX = (chartWidth - legendWidth)/2;

  var axes = svg.append('g')
    .attr('clip-path', 'url(#axes-clip)');

  axes.append('g')
    .attr('class', 'x axis')
    .attr('transform', 'translate(0,' + chartHeight + ')')
    .call(xAxis)
    .append('text')
      .attr('y', -20)
      .attr('x', chartWidth-40)
      .attr('dy', '.71em')
      .text('Time');

  axes.append('g')
    .attr('class', 'y axis')
    .call(yAxis);

  var legend = svg.append('g')
    .attr('class', 'legend')
    .attr('transform', 'translate(' + (legendStartX) + ', 0)');

  legend.append('rect')
    .attr('class', 'legend-bg')
    .attr('width',  legendWidth)
    .attr('height', legendHeight);

  legend.append('path')
    .attr('class', 'current-line')
    .attr('d', 'M10,30L70,30');

  legend.append('text')
    .attr('x', 10)
    .attr('y', 20)
    .text(title1);

  legend.append('path')
    .attr('class', 'other-line')
    .attr('d', 'M165,30L100,30');

  legend.append('text')
    .attr('x', 100)
    .attr('y', 20)
    .text(title2);

}

function getPathValue(y, data, section_idx, value_idx) {

	var value1 = data.value1;
	var value2 = data.value2;

	if (section_idx == 0) {

		// value1 and value2 lines

		if ( (value1 === 'undefined' || isNaN(value1)) && value_idx==1) {
			return NaN;
		}
		if ((value2 === 'undefined' || isNaN(value2)) && value_idx==2) {
			return NaN;
		}

		return (value_idx==1) ? y(value1) : y(value2);

	} else {

		// upper and lower sections

		if (value1 === 'undefined' || isNaN(value1)) {
			value1 = value2;
		}

		if (value2 === 'undefined' || isNaN(value2)) {
			value2 = value1;
		}

		if (section_idx == 1) {

			if (value_idx == 2) {
				// return the highest one
				return (value2 > value1) ? y(value2) : y(value1);
			} else {
				// return the lowest one
				return (value2 > value1) ? y(value1) : y(value2);
			}

		} else {

			if (value_idx == 1) {
				// return the highest one
				return (value2 > value1) ? y(value2) : y(value1);
			} else {
				// return the lowest one
				return (value2 > value1) ? y(value1) : y(value2);
			}


		}

	}

}

function drawPaths (svg, data, x, y) {
  
  var upperArea = d3.svg.area()
	.interpolate('basis')
	.x (function (d) { return x(d.date) || 1; })
	.y0(function (d) { return (getPathValue(y, d,1,2)); })
	.y1(function (d) { return (getPathValue(y, d,1,1)); });

  var currentLine = d3.svg.line()
	.interpolate('basis')
	.defined(d => !isNaN(getPathValue(y, d,0,1)))
	.x(function (d) { return x(d.date); })
	.y(function (d) { return (getPathValue(y, d,0,1)); });

	//  var otherLine = d3.svg.line()
	//	.interpolate('basis')
	//	.x(function (d) { return x(d.date); })
	//	.y(function (d) { return (getPathValue(y, d,0,2)); });

  var lowerArea = d3.svg.area()
	.interpolate('basis')
	.x (function (d) { return x(d.date) || 1; })
	.y0(function (d) { return (getPathValue(y, d,2,1)); })
	.y1(function (d) { return (getPathValue(y, d,2,2)); });

  svg.datum(data);

  svg.append('path')
	.attr('class', 'area upper')
	.attr('d', upperArea)
	.attr('clip-path', 'url(#rect-clip)');

  svg.append('path')
	.attr('class', 'area lower')
	.attr('d', lowerArea)
	.attr('clip-path', 'url(#rect-clip)');

  svg.append('path')
	.attr('class', 'current-line')
	.attr('d', currentLine)
	.attr('clip-path', 'url(#rect-clip)');

	//    svg.append('path')
	//	.attr('class', 'other-line')
	//	.attr('d', otherLine)
	//	.attr('clip-path', 'url(#rect-clip)');

}

function addMarker (marker, svg, chartHeight, x) {

  var radius = 24,
      xPos = x(marker.date) - radius - 3,
      yPosStart = chartHeight - radius - 3,
      yPosEnd = (marker.type === 'Now' ? -5 : chartHeight-100);

  var markerG = svg.append('g')
    .attr('class', 'marker '+marker.type.toLowerCase())
    .attr('transform', 'translate(' + xPos + ', ' + yPosStart + ')')
    .attr('opacity', 0);

  markerG.transition()
    .duration(transition_delay)
    .attr('transform', 'translate(' + xPos + ', ' + yPosEnd + ')')
    .attr('opacity', 1);

  markerG.append('path')
    .attr('d', 'M' + radius + ',' + (chartHeight-yPosStart) + 'L' + radius + ',' + (chartHeight-yPosStart))
    .transition()
      .duration(transition_delay)
      .attr('d', 'M' + radius + ',' + (chartHeight-yPosEnd) + 'L' + radius + ',' + (radius*2));

  markerG.append('circle')
    .attr('class', 'marker-bg')
    .attr('cx', radius)
    .attr('cy', radius)
    .attr('r', radius);

  var marker_text = marker.type;

  if (marker.caption != '') {
  	marker_text = marker.caption;
  }

  markerG.append('text')
    .attr('x', radius)
    .attr('y', radius*1.2)
    .text(marker_text);

}

function startTransitions (svg, chartWidth, chartHeight, rectClip, markers, x) {

  rectClip.transition()
    .duration(transition_delay*markers.length)
    .attr('width', chartWidth);

  markers.forEach(function (marker, i) {
    setTimeout(function () {
      addMarker(marker, svg, chartHeight, x);
    }, transition_delay + (transition_delay/2)*i);
  });
  
}

function makeChart (data, markers, div_id, title1, title2) {

	/*

		DATA must be in the format of a list of dict objects:

		var data = [
		  {
			"date": {datetime_obj},
			"value1": 4233,
			"value2": 5559
		  }
		]

		- 'date' must a javascript Date object (see more below)
		- 'value1' is the original value
		- 'value2' is the "different" value
		
		var parseDate  = d3.time.format("%Y-%m-%dT%H:%M:%S").parse;

		The date object can be derived from a ISO 8601 datetime string:
		e.g.: parseDate("2014-08-01T01:09:00")

	  	There are two types of markers:
	  	- 'Now' which specifies the current time on the chart
	  	- 'Other' which can be used to specify any other item

		These can be changed in the CSS...

	  	MARKERS must be in the following format:
	  
		  var markers = [
			  {
				"date": parseDate("2014-08-01T01:02:00"),
				"type": "Other",
				"caption": "caption A"
			  },
  			  {
				"date": parseDate("2014-08-01T01:12:00"),
				"type": "Now",
				"caption": "caption B"
			  }		 	 
		  ];	  

	*/
	
	var svg_canvas = d3.select('div#' + div_id);

	var svgWidth = (window.innerWidth
			|| document.documentElement.clientWidth
			|| document.body.clientWidth) * 0.9;
			
	var svgHeight = (window.innerHeight
			|| document.documentElement.clientHeight
			|| document.body.clientHeight) * 0.7;

	var margin = { top: 10, right: 50, bottom: 50, left: 100 };
  	var chartWidth  = svgWidth  - margin.left - margin.right;
  	chartHeight = svgHeight - margin.top  - margin.bottom;

  	var legend_range_multiplier = (1.1+(legendHeight/chartHeight));

  	var x = d3.time.scale().range([0, chartWidth])
            .domain(d3.extent(data, function (d) { return d.date; })),
    	y = d3.scale.linear().range([chartHeight, 0])
            .domain([0, d3.max(data, function (d) { 
            	if (d.value1 > d.value2) 
            		{ return d.value1; } else { return d.value2; } }) * legend_range_multiplier ]);

	var xAxis = d3.svg.axis().scale(x).orient('bottom')
                .innerTickSize(-chartHeight).outerTickSize(0).tickPadding(10),
    	yAxis = d3.svg.axis().scale(y).orient('left')
                .innerTickSize(-chartWidth).outerTickSize(0).tickPadding(10);

	var svg = svg_canvas.append('svg')
    	.attr('width',  svgWidth)
    	.attr('height', svgHeight)
    	.append('g')
      	.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

	// clipping to start chart hidden and slide it in later
  	var rectClip = svg.append('clipPath')
    	.attr('id', 'rect-clip')
    	.append('rect')
      	.attr('width', 0)
      	.attr('height', chartHeight);

	// add the axes and legend
  	addAxesAndLegend(svg, xAxis, yAxis, margin, chartWidth, chartHeight, title1, title2);
	
	// draw the chart
  	drawPaths(svg, data, x, y);
  
	// show the chart along with the markers
  	startTransitions(svg, chartWidth, chartHeight, rectClip, markers, x);
  	
}
