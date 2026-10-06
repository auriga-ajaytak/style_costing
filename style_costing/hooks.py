app_name = "style_costing"
app_title = "Style Costing"
app_publisher = "Auriga IT"
app_description = "Apparel style master and style costing for ERPNext"
app_email = "ajay@aurigait.com"
app_license = "gpl-3.0"

# Apps
# ------------------

required_apps = ["erpnext"]

# Includes in <head>
# ------------------

# Shared Style Master / Style Costing form logic. In v13 this was three
# near-identical copies wired up through doctype_js; it is now one bundle.
app_include_js = "style_costing.bundle.js"

# include js in doctype views
doctype_js = {
	"Item": "public/js/item.js",
	"Quotation": "public/js/quotation.js",
}

doctype_list_js = {
	"Item": "public/js/item_list.js",
}

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Item": "style_costing.docevents.item.StyleItem",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Quotation": {
		"validate": "style_costing.docevents.quotation.validate",
	},
	"Item": {
		"validate": "style_costing.docevents.item.validate",
	},
}

# Fixtures
# --------
# Structural defaults only: generic garment-industry masters every install
# needs. Site-specific data such as merchandisers is not shipped; sample
# records for trials live in style_costing/demo. The v13 app also exported a
# site-wide dump of all 34 Workspaces, which would overwrite the standard
# ERPNext ones - the Styling workspace is a proper app workspace here instead.

fixtures = [
	{"dt": "Cost Head"},
	{"dt": "Cost Type"},
	{"dt": "Production Process"},
	{"dt": "Season"},
	{"dt": "Segment"},
	{"dt": "Value Addition"},
]
