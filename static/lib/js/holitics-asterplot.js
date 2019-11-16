// holitics-asterplot.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project
//
// Multi-bar barchart utilizing the d3 charting library
//
// dependencies:
//	 - JS:  v4 of the d3 charting library (d3.v4.min.js)
// 	 - JS: 	app-specific caller JS file
//	 - CSS: holitics-asterplot-1.0.css
//   - tooltips: d3tip-v4.js

var width = 350,
    height = 350,
    radius = Math.min(width, height) / 2,
    innerRadius = 0.3 * radius;

var pie = d3.layout.pie()
    .sort(null)
    .value(function(d) { return d.width; });

var tip = d3.tip()
  .attr('class', 'd3-tip')
  .offset([0, 0])
  .html(function(d) {
    return "" + d.data.label + "<span style='padding-left:25px;color:orangered'> (" + d.data.score + "%)</span>";
  });

var arc = d3.svg.arc()
  .innerRadius(innerRadius)
  .outerRadius(function (d) {
  	score = d.data.score
  	if (score>100) {
  		score = 100;
	}  		
    return (radius - innerRadius) * (score / 100.0) + innerRadius; 
  });

var outlineArc = d3.svg.arc()
        .innerRadius(innerRadius)
        .outerRadius(radius);

var svg = d3.select("body").append("svg")
	.attr("class", "fade-in")
	.attr("style", "display:block; margin:auto;")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

svg.call(tip);

// colorful
var palette_1 = ["#4D9DB4","#6CC4A4","#9CD6A4","#C7E89E","#EAF195","#FAE38C","#FEC574","#FB9F59","#F47245"];
// grey/blue
var palette_2 = ["#74879E","#8091A6","#8D9CAF","#99A7B8","#A6B2C1","#B3BDCA","#BFC8D2","#CCD3DB","#D9DEE4"];

function buildPlot(data) {

	var color_id = 0;
	
  data.forEach(function(d) {
    d.id     =  d.id;
    d.order  = +d.order;
    d.color  =  palette_2[color_id];
    color_id++;
    if (color_id>9) {
    	color_id = 0;
    }
    d.weight = +d.weight;
    d.score  = +d.score;
    d.width  = +d.weight;
    d.label  =  d.label;
  });
  
  // for (var i = 0; i < data.score; i++) { console.log(data[i].id) }
  
  var path = svg.selectAll(".solidArc")
      .data(pie(data))
    .enter().append("path")
      .attr("fill", function(d) { return d.data.color; })
      .attr("class", "solidArc")
      .attr("stroke", "gray")
      .attr("d", arc)
      .on('mouseover', tip.show)
      .on('mouseout', tip.hide);

  var outerPath = svg.selectAll(".outlineArc")
      .data(pie(data))
    .enter().append("path")
      .attr("fill", "none")
      .attr("stroke", "none")
      .attr("class", "outlineArc")
      .attr("d", outlineArc);  


  // calculate the weighted mean score
  var score = 
    data.reduce(function(a, b) {
      return a + (b.score * b.weight); 
    }, 0) / 
    data.reduce(function(a, b) { 
      return a + b.weight; 
    }, 0);

  svg.append("svg:text")
    .attr("class", "aster-score")
    .attr("fill", "aliceblue")
    .attr("dy", ".45em")
    .attr("font", "40px")
    .attr("text-anchor", "middle") // text-align: right
    .text(Math.round(score) + "%");

};