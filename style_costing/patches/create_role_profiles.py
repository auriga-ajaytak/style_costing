from style_costing.setup import create_role_profiles


def execute():
	"""Sites installed before the role profiles existed."""
	create_role_profiles()
