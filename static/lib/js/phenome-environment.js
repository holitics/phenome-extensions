// phenome-environment.js
// Copyright (c) 2019 Nicholas Saparoff, Phenome Project
//
// ENV settings for Phenome JS

// DEFAULT TO NO CDN. We will use the CDN if it is available.
// To turn off the check and HARD CODE use of the CDN,
// set the following to true and 1.

var CDN_check_disabled = false;
var use_CDN = 0;

var CDN_TEST_URL = 'https://s3.amazonaws.com/phenome-cdn/images/phenome_favicon.png';
var CDN_URL_SECURE = 'https://s3.amazonaws.com/phenome-cdn';

function checkSDN(sdnUrl, callback){
       function getRequest(url){
           return $.ajax({  // Makes a quick GET request for the URL
               	url: url,
        		type: 'GET',
        		crossDomain: true
           });
        };
        getRequest(sdnUrl)
        .done(function(){
            callback(true); // url exists
        })
        .fail(function(){
            callback(false); // something failed
        });
 };
 
if (CDN_check_disabled == false) {

	checkSDN(CDN_TEST_URL, function(exists) {
		if (exists) {
			use_CDN = 1;
			//alert("CDN is available!");
		} else {
			use_CDN = 0;
			//alert("CDN is NOT available!");
		}
	});

}

function get_image_url(image) {

	var image_prefix_url = '/static';
	
	if (use_CDN==1) {
		image_prefix_url = CDN_URL_SECURE;
	}

    // make sure that the full URL is formed correctly

	var image_url = image;

	if (image_url.startsWith('/') == false) {
		image_url = '/' + image_url;
	}

	if (image_url.startsWith('/images') == false) {
		image_url = '/images' + image_url;
	}

	// finally, return the full URL to the image
	return image_prefix_url + image_url;
	

}