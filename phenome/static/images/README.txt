All CLASSTYPE and SUBCLASSTYPE ICONS for ALL APPLICATIONS MUST BE PLACED HERE.
In addition, during the packaging process, all images from /static/apps/{app_name}/lib/img
are also copied to this folder in the package.

CDN: Images in this folder will be uploaded to the phenome-cdn S3 repository. 
By default, they will be publicly accessible using the CDN using the URL:

https://s3.amazonaws.com/phenome-cdn/images/XXXX.png

To change the base CDN URL, put the "cdn_base_url" property into the core.ini file in the MISC section:

[MISC]
cdn_base_url: https://s3.amazonaws.com/phenome-cdn/

-----

Recommendations for Classtype or Model ICON PNG files:

Entire image dimensions should be a perfect square. 
200x200 pixels maximum size. 64x64 pixels minimum size.
White (preferred) or transparent background.
