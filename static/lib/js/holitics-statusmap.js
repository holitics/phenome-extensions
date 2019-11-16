// holitics-statusmap.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project
//
// Object Health Status-Map utilizing the d3 charting library
// references the holitics-statusmap-1.0.css file.

// Fix map for IE
if (!('map' in Array.prototype)) { 
  Array.prototype.map = function (mapper, that /*opt*/) { 
    var other = new Array(this.length); 
    for (var i = 0, n = this.length; i < n; i++) 
      if (i in this) 
        other[i] = mapper.call(that, this[i], i, this); 
    return other; 
  }; 
};

var browser = BrowserDetect;

if (isOldBrowser()) {
	$('#old_browser_msg').show();
	$('#wtf').hide();
	$('fieldset#state').addClass('ff3');
	$('#ie8_percents').addClass('ff3');
	$('#poweredby.old_browsers').show();
}

var buckets = 11;
var colorScheme = 'healthstatusdark';

var data;
var classtype_dict = {};
var current_columns = 24;
var current_rows = 7;	
var object_dialog_show_details = 1;
var object_dialog_header_only = 0;

var face_class = 'face';
var tile_class = 'tile';
var tile_width = 36;
var column_wrap_min_x = 8;
var has_large_tiles = false;


function getDeviceDetails(array_id) {

	obj = data['data'][array_id]['t0']
	obj_id = obj[0]
	obj_health_score = obj[1]
	obj_descr = obj[2]
	obj_model_id = obj[3]
	console.log('statusmap hover - object: ' + obj_descr + ', id=' + obj_id + ', model_id=' + obj_model_id );
	txt = obj_descr + "  [id=" + obj_id + "]";

	return txt;		
		
}

function getDeviceObjectId(array_id) {

	obj = data['data'][array_id]['t0']
	return obj_id;

}

function buildStatusMap (json, classtypes_json) {

	var classtypes = classtypes_json['data'];
	
	for (var i = 0; i < classtypes.length; i++){
   		var obj = classtypes[i];
   		classtype_id = obj['value'];
   		classtype_name = obj['id'];
   		classtype_dict[classtype_id] = classtype_name;
	}

	d3.select('#vis').classed(colorScheme, true);

	data = json;
	no_data = false;

	if (data!=null) {
		total_cells = data['data'].length;
		if (total_cells == null || total_cells == 0) {
			no_data = true;
		}
	} else {
		no_data = true;
	}

	if (no_data) {
		build_no_result('', false);
		return;
	}

	createTiles();
	paintTiles();
	
	/* ************************** */
		
	// tiles mouseover events
	$('#tiles td').hover(function() {
	
		$(this).addClass('sel');
				
		var cell_id = $(this).attr('id');
		console.log('hovering over cell: ' + cell_id);
		
		var tmp = cell_id.split('o'),
			array_id = parseInt(tmp[1]);

		// should we add a tooltip?		
		if (data!=null && array_id < data['data'].length) {

			if (has_large_tiles == false) {
				// we will need tooltips since there is no IDfying info
				$(this).tooltip({
					delay: 100,
					placement: "bottom",
					title: getDeviceDetails(array_id),
					html: true
				}); 
			}

			$(this).popover({
				placement: "bottom",
				title: getDeviceDetails(array_id),			
				html: true,
				content: function() {
					return build_object_dialog(getDeviceObjectId(array_id));
        		}
			}); 
  

		}
		
	}, function() {
		
		$(this).removeClass('sel');
		
	});
	
}

/* ************************** */

function isOldBrowser() {

	var result = false;
	if (browser.browser === 'Explorer' && browser.version < 9) {
		result = true;
	} else if (browser.browser === 'Firefox' && browser.version < 4) {
		result = true;
	}
	
	//console.log(result);
	
	return result;
}

/* ************************** */

function getCalcs() {
	
	var min = 0,
		max = 10;
	
	return {'min': min, 'max': max};
	
};

function paintTiles() {
	
	var calcs = getCalcs(),
		range = [];
	
	for (var i = 1; i <= buckets; i++) {
		range.push(i);
	}
	
	var bucket = d3.scale.quantize().domain([0, calcs.max > 0 ? calcs.max : 1]).range(range),
		side = d3.select('#tiles').attr('class');
	
	
	if (side === 'front') {
		side = 'back';
	} else {
		side = 'front';
	}
	
	var x = 0;
	var div_id = null;
	
	for (var d = 0; d < current_rows; d++) {
		for (var h = 0; h < current_columns; h++) {

			// get the ID of the TD
			td_id = 'o'+x;
			
			// get the div id of the face back
			div_id = td_id + '_fb';

			if (data==null) {
				obj_value = -1;
			} else {
				obj = data['data'][x];
				if (obj === undefined) {
					obj_value = -1;
				} else {
					// get the object ID and value
					obj_id = obj['t0'][0];
					obj_value = obj['t0'][1];
				}
			}
			
			var sel = '#' + td_id + ' .' + tile_class + ' .' + side;
			
			// erase all previous bucket designations on this cell
			for (var i = 0; i <= buckets; i++) {
				var cls = 'q' + i + '-' + buckets;
				d3.select(sel).classed(cls , false);
			}
			
			// set new color designation for this cell
			var cls = 'q' + (obj_value >= 0 ? (obj_value+1) : 0) + '-' + buckets;
			
			d3.select(sel).classed(cls, true);
		

			x++;
			
		}
	}
	
	flipTiles();
	
}


/* ************************** */

function flipTiles() {

	var oldSide = d3.select('#tiles').attr('class'),
		newSide = '';
	
	if (oldSide == 'front') {
		newSide = 'back';
	} else {
		newSide = 'front';
	}
	
	var flipper = function(id, side) {
		return function() {
			var sel = '#o' + id + ' .' + tile_class,
				rotateY = 'rotateY(180deg)';
			
			if (side === 'back') {
				rotateY = 'rotateY(0deg)';	
			}
			if (browser.browser === 'Safari' || browser.browser === 'Chrome') {
				d3.select(sel).style('-webkit-transform', rotateY);
			} else {
				d3.select(sel).select('.' + oldSide).classed('hidden', true);
				d3.select(sel).select('.' + newSide).classed('hidden', false);
			}
				
		};
	};
	

	var i = 0;
	
	for (var h = 0; h < current_rows; h++) {
		for (var d = 0; d < current_columns; d++) {
			var side = d3.select('#tiles').attr('class');
			setTimeout(flipper(i, side), (h * 20) + (d * 20) + (Math.random() * 100));
			i++;
		}
	}
	
	d3.select('#tiles').attr('class', newSide);
	
}


/* ************************** */

function createTiles() {


	var html = '<table id="tiles" class="front">';

	html += '<tr><th><div>&nbsp;</div></th>';

	// default size
	rows = 7
	columns = 24

	var i = 0;
	var total_cells = rows * columns;
	if (data!=null) {
		total_cells = data['data'].length;
	}

	// get the width and height of the client area
	var div_vis = document.getElementById('vis');
	// use 80% of what is available
	var client_width = div_vis.clientWidth * 0.85;
	var client_height = div_vis.clientHeight * 0.75;

	if (total_cells <= 20) {
		// we will shift to "large" tiles
		face_class = 'face_large';
		tile_class = 'tile_large';
		tile_width = 152;
		has_large_tiles = true;
	}
	
	// get the number of columns that can fit	
	columns_can_fit = Math.floor(client_width / tile_width);

	// set the wrap min based on the columns
	column_wrap_min_x = columns_can_fit; //4;
	
	// determine number of rows
	var rows_calc = Math.floor(total_cells/columns_can_fit);
	var r = (total_cells % columns_can_fit);
	if (r>0) {
		rows_can_fit = rows_calc+1;
	} else {
		rows_can_fit = rows_calc;
	} 

	// set the minimum number of rows to "2" so it does not look stupid
	if (rows_can_fit<2) {
		rows_can_fit = 2;
	}

	// calc the total cells to show
	total_cells = rows_can_fit * columns_can_fit;
	
	// finally, set the current number of columns/rows for this tiled area
	current_columns = columns_can_fit;
	current_rows = rows_can_fit;
	
	var tile_descr = '';

	// and draw it
	for (var d = 0; d < current_rows; d++) {
		html += '<tr class="d' + d + '">';

		for (var h = 0; h < current_columns; h++) {
		
			td_id = 'o' + i;
			div_id_fb = td_id + '_fb';
			div_id_ff = td_id + '_ff';
			
			obj = data['data'][i];
			if (obj === undefined) {
				obj_value = -1;
				obj_name = '';
				obj_model_id = 0;
				obj_classtype_id = 0;
				obj_classtype_text = '';
				obj_power_state = -1;
			} else {
				// get the object ID and value
				obj_id = obj['t0'][0];
				obj_value = obj['t0'][1];
				obj_name = obj['t0'][2];
				obj_model_id = obj['t0'][3];
				obj_classtype_id = obj['t0'][4];
				obj_classtype_text = classtype_dict[obj_classtype_id]
				obj_power_state = obj['t0'][5];
			}
			
			tile_descr = '';
			tile_icon = '';
			obj_style = '';

			if (obj_power_state == 1) {
				// the object is "POWERED_OFF", so change the opacity setting
				obj_style = 'opacity: 0.25;';
			} else {
				obj_style = 'opacity: 1.0;';
			}
			
			if (obj_classtype_text != '') {
				tile_descr = tile_descr + obj_classtype_text + '<BR>';
				tile_icon_url = '/static/images/' + obj_classtype_text.toLowerCase() + '.png';
				// append to the obj style
				obj_style = obj_style + 'background-image: url(' + tile_icon_url + ');';
			}
		
			if (obj_name != '') {
				tile_descr = tile_descr + obj_name;
			}
					
			html += '<td id="' + td_id + '" class="' + td_id + '"><div class="' + tile_class + '">';
			html += '		<div id="' + div_id_ff + '" class="' + face_class + ' front"></div>';
			html += '		<div id="' + div_id_fb + '" class="' + face_class + ' back" style="' + obj_style + '" >' + tile_descr + '</div>';
			html += '</div></td>';
			
			i++;
			
			// column wrap max for small total-cell count
			if (i>total_cells && i>=column_wrap_min_x && d==0) {
				current_columns = h+1;
				break;
			}
			
		}
		html += '</tr>';
		
		// row wrap max for small total-cell count
		if (i>total_cells) {
			current_rows = d+1;
			break;
		}
		
	}
	
	html += '</table>';
	
	d3.select('#vis').html(html);

	
}

