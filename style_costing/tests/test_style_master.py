# Copyright (c) 2022, Auriga and contributors
# See license.txt
"""End-to-end checks for the v13 -> v16 port of Style Master."""

from unittest.mock import patch

import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests import IntegrationTestCase

from style_costing import approval, bom, demo, queries, setup
from style_costing.style_costing.doctype.fabric_process_route import (
	fabric_process_route as fpr,
)

from style_costing.style_costing.report.bom_costing_reconciliation.bom_costing_reconciliation import (
	execute as reconciliation,
)
from style_costing.style_costing.report.fabric_and_trim_consumption.fabric_and_trim_consumption import (
	execute as consumption,
)
from style_costing.style_costing.report.style_order_tracking.style_order_tracking import (
	execute as order_tracking,
)
from style_costing.style_costing.report.style_costing_summary.style_costing_summary import (
	execute as costing_summary,
)
from style_costing.style_costing.doctype.style_costing_settings.style_costing_settings import (
	get_style_defaults,
)

LINK_QUERY_ARGS = {"txt": "", "searchfield": "name", "start": 0, "page_len": 20}

# This app overrides Item.autoname, so every Item gets a generated code
# (F-0000001, T-0000001, ...). ERPNext's shared test records expect to keep the
# codes they ask for (_Test Item and friends), so this suite opts out of them
# and builds exactly the fixtures it needs.
EXTRA_TEST_RECORD_DEPENDENCIES = []


class TestStyleMaster(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.fabric_group = _mk(
			"Item Group",
			item_group_name="SMC Test Fabric",
			parent_item_group="All Item Groups",
			is_group=0,
			group_category="Fabric",
		)
		cls.trims_group = _mk(
			"Item Group",
			item_group_name="SMC Test Trims",
			parent_item_group="All Item Groups",
			is_group=0,
			group_category="Trims",
		)
		cls.fabric_item = _mk(
			"Item",
			item_name="SMC Test Poplin",
			item_group=cls.fabric_group,
			stock_uom="Meter",
			is_stock_item=0,
			composition="100% Cotton",
		)
		cls.trim_item = _mk(
			"Item",
			item_name="SMC Test Button",
			item_group=cls.trims_group,
			stock_uom="Nos",
			is_stock_item=0,
			composition="Polyester",
		)
		cls.customer = _mk("Customer", customer_name="SMC Test Buyer")
		cls.product = _mk("Product", product_name="SMC Mens Shirt")

	# --- Item override -------------------------------------------------
	def test_item_code_series_follows_item_group_category(self):
		"""StyleItem.autoname prefixes the item code from Item Group.group_category."""
		self.assertTrue(self.fabric_item.startswith("F-"), self.fabric_item)
		self.assertTrue(self.trim_item.startswith("T-"), self.trim_item)

	def test_item_validate_sets_qr_code(self):
		self.assertTrue(frappe.db.get_value("Item", self.fabric_item, "qr_code"))

	# --- the style DocType ------------------------------------------------
	def test_style_master_lifecycle(self):
		doc = self._build("Style Master")
		self.assertEqual(len(doc.fabric_table), 1)
		self.assertEqual(len(doc.trims_table), 1)
		doc.submit()
		self.assertEqual(doc.docstatus, 1)
		doc.cancel()
		self.assertEqual(doc.docstatus, 2)

		amended = frappe.copy_doc(doc)
		amended.amended_from = doc.name
		amended.docstatus = 0
		amended.insert()
		self.assertEqual(amended.amended_from, doc.name)

	def test_style_master_uses_native_tabs(self):
		"""The v13 jQuery tab overlay is replaced by real Tab Break fields."""
		tabs = [f.label for f in frappe.get_meta("Style Master").fields if f.fieldtype == "Tab Break"]
		self.assertEqual(len(tabs), 10, f"{tabs}")
		self.assertEqual(tabs[0], "Style Details")

	def test_amended_from_points_at_own_doctype(self):
		"""v13 pointed Style Costing's amended_from at Style Master."""
		df = frappe.get_meta("Style Master").get_field("amended_from")
		self.assertEqual(df.options, "Style Master")

	def test_style_details_tab_carries_the_header_fields(self):
		"""The header fields belong on Style Details, not scattered across later tabs."""
		meta = frappe.get_meta("Style Master")
		order = [f.fieldname for f in meta.fields]
		tab_idx = [i for i, f in enumerate(meta.fields) if f.fieldtype == "Tab Break"]
		first_tab = set(order[tab_idx[0]:tab_idx[1]])
		for fieldname in ("customer", "item", "naming_series", "style_number", "merchandiser", "season", "segment"):
			self.assertIn(fieldname, first_tab, f"{fieldname} is not on the Style Details tab")

	# --- whitelisted endpoints the client script calls -------------------
	def test_link_queries(self):
		self.assertTrue(queries.fabric_item_group_wise_items(doctype="Item", filters=None, **LINK_QUERY_ARGS))
		self.assertTrue(queries.trims_item_group_wise_items(doctype="Item", filters=None, **LINK_QUERY_ARGS))
		self.assertTrue(
			queries.value_addition_fabric(
				doctype="Item", filters={"fabrics": [self.fabric_item]}, **LINK_QUERY_ARGS
			)
		)
		# a fabric filter that matches nothing must not leak every fabric
		self.assertFalse(
			queries.value_addition_fabric(
				doctype="Item", filters={"fabrics": ["does-not-exist"]}, **LINK_QUERY_ARGS
			)
		)

	def test_get_doc_wise_columns_reads_live_meta(self):
		"""v13 read the DocType JSON off disk, ignoring Customize Form changes."""
		fields = queries.get_doc_wise_columns("fabric")["fields"]
		self.assertTrue(any(f["fieldname"] == "fabric_name" for f in fields))

	# --- process route ---------------------------------------------------
	def test_save_process_route_replaces_rows(self):
		style = self._build("Style Master")
		fpr.saveProcessRoute(
			stylemaster=style.name,
			fabric_name=self.fabric_item,
			process_route=[{"fabric_name": self.fabric_item, "process_type": "Dyeing"}],
		)
		fpr.saveProcessRoute(
			stylemaster=style.name,
			fabric_name=self.fabric_item,
			process_route=[{"fabric_name": self.fabric_item, "process_type": "Washing"}],
		)
		rows = frappe.get_all("Fabric Process Route", filters={"parent": style.name}, pluck="process_type")
		self.assertEqual(rows, ["Washing"])

	def test_save_process_route_rejects_unknown_parent(self):
		"""v13 interpolated `stylemaster` straight into a DELETE statement."""
		with self.assertRaises(frappe.ValidationError):
			fpr.saveProcessRoute(
				stylemaster="x' OR '1'='1",
				fabric_name=self.fabric_item,
				process_route=[{"process_type": "X"}],
			)

	# --- operation bulletin ----------------------------------------------
	def test_operation_bulletin_scaffold(self):
		_mk("Production Category", category_name="SMC Sewing")
		rows = frappe.new_doc("Operation Bulletin").load_category()
		self.assertEqual(len(rows) % 3, 0)
		self.assertTrue(any(r["category"] == "Total" for r in rows))

	# --- settings ---------------------------------------------------------
	def test_style_is_named_from_the_neutral_default_series(self):
		self.assertTrue(self._build("Style Master").name.startswith("STY-"))

	def test_settings_series_names_new_styles(self):
		settings = frappe.get_doc("Style Costing Settings")
		self.addCleanup(_set_series, settings.style_naming_series)
		_set_series("SMCT-.####")
		name = self._build("Style Master").name
		self.assertTrue(name.startswith("SMCT-"), name)

	def test_settings_reject_an_invalid_series(self):
		settings = frappe.get_doc("Style Costing Settings")
		settings.style_naming_series = "NO DOT ####"
		self.assertRaises(frappe.ValidationError, settings.save)

	def test_style_defaults_come_from_settings(self):
		settings = frappe.get_doc("Style Costing Settings")
		settings.default_style_rate = 2.5
		settings.default_efficiency = 60
		settings.set("default_cost_heads", [{"cost_head": "COMMISSION", "based_on": "Rate", "rate_our": 10}])
		settings.save()
		defaults = get_style_defaults()
		self.assertEqual((defaults["style_rate"], defaults["efficiency"]), (2.5, 60))
		self.assertEqual([row["cost_head"] for row in defaults["cost_heads"]], ["COMMISSION"])
		self.assertEqual(defaults["cost_heads"][0]["rate_our"], 10)

	def test_item_codes_can_be_left_to_erpnext(self):
		self.addCleanup(_set_setting, "keep_erpnext_item_codes", 0)
		_set_setting("keep_erpnext_item_codes", 1)
		item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "SMC-KEPT-CODE",
				"item_name": "SMC Kept Code",
				"item_group": self.fabric_group,
				"stock_uom": "Meter",
				"is_stock_item": 0,
				"composition": "100% Cotton",
			}
		).insert()
		self.assertEqual(item.name, "SMC-KEPT-CODE")

	# --- item override clash ------------------------------------------------
	def test_no_conflict_when_only_this_app_overrides_item(self):
		self.assertIsNone(setup.get_item_override_conflict())

	def test_conflict_reported_when_another_app_wins_item(self):
		with _item_overrides(setup.ITEM_CONTROLLER, "other_app.overrides.OtherItem"):
			self.assertIn("other_app.overrides.OtherItem", setup.get_item_override_conflict())

	def test_conflict_reported_when_this_app_wins_item(self):
		with _item_overrides("other_app.overrides.OtherItem", setup.ITEM_CONTROLLER):
			self.assertIn("ignored", setup.get_item_override_conflict())

	def test_untagged_item_groups_are_counted(self):
		before = setup.untagged_item_groups()
		# Group Category is mandatory, so only groups older than the app lack one
		group = _mk(
			"Item Group",
			item_group_name="SMC Untagged",
			parent_item_group="All Item Groups",
			is_group=0,
			group_category="Fabric",
		)
		frappe.db.set_value("Item Group", group, "group_category", None)
		self.assertEqual(setup.untagged_item_groups(), before + 1)
		self.assertTrue(any("Group Category" in w for w in setup.setup_warnings()))

	# --- charts, notifications, onboarding --------------------------------
	def test_standard_records_are_installed(self):
		for doctype, name in (
			("Dashboard Chart", "Styles by Buyer"),
			("Dashboard Chart", "Styles by Season"),
			("Dashboard Chart", "Styles by Merchandiser"),
			("Notification", "Style Awaiting Approval"),
			("Notification", "Style Approved"),
			("Module Onboarding", "Style Costing Onboarding"),
			("Onboarding Step", "Tag Item Groups"),
			("Number Card", "Styles in Progress"),
		):
			self.assertTrue(frappe.db.exists(doctype, name), f"{doctype} {name}")

	def test_costed_style_notifies_the_costing_manager(self):
		self.addCleanup(_set_setting, "enable_approval_workflow", 0)
		_set_setting("enable_approval_workflow", 1)
		manager = _mk_user("smc-costing-manager@example.com", "Costing Manager")
		style = self._build("Style Master")
		apply_workflow(style, "Mark Costed")
		logs = frappe.get_all(
			"Notification Log", filters={"document_name": style.name, "for_user": manager}, pluck="subject"
		)
		self.assertTrue(any("awaiting approval" in (s or "") for s in logs), logs)

	# --- roles ------------------------------------------------------------
	def test_roles_and_change_tracking(self):
		meta = frappe.get_meta("Style Master")
		self.assertTrue(meta.track_changes)
		self.assertTrue(frappe.get_meta("Operation Bulletin").track_changes)
		by_role = {p.role: p for p in meta.permissions}
		self.assertTrue(by_role["Costing Manager"].submit)
		self.assertTrue(by_role["Merchandiser"].write)
		self.assertFalse(by_role["Merchandiser"].submit)
		self.assertFalse(by_role["Production Planner"].write)
		for role in ("Costing Manager", "Merchandiser", "Production Planner"):
			self.assertTrue(frappe.db.exists("Role", role), role)

	def test_style_master_has_a_company(self):
		self.assertEqual(frappe.get_meta("Style Master").get_field("company").options, "Company")

	# --- approval workflow ------------------------------------------------
	def test_approval_workflow_is_off_until_enabled(self):
		self.assertFalse(frappe.db.get_value("Workflow", approval.WORKFLOW, "is_active"))

	def test_approval_workflow_runs_draft_to_quoted(self):
		self.addCleanup(_set_setting, "enable_approval_workflow", 0)
		_set_setting("enable_approval_workflow", 1)
		style = self._build("Style Master")
		self.assertEqual(style.workflow_state, "Draft")
		for action, state, docstatus in (
			("Mark Costed", "Costed", 0),
			("Send Back", "Draft", 0),
			("Mark Costed", "Costed", 0),
			("Approve", "Approved", 1),
			("Mark Quoted", "Quoted", 1),
			("Cancel", "Cancelled", 2),
		):
			style = apply_workflow(style, action)
			self.assertEqual((style.workflow_state, style.docstatus), (state, docstatus))

		_set_setting("enable_approval_workflow", 0)
		self.assertFalse(frappe.db.get_value("Workflow", approval.WORKFLOW, "is_active"))

	def test_merchandiser_cannot_approve(self):
		allowed = {
			(t.action, t.allowed) for t in frappe.get_doc(_workflow_doc()).transitions
		}
		self.assertIn(("Mark Costed", "Merchandiser"), allowed)
		self.assertNotIn(("Approve", "Merchandiser"), allowed)

	# --- buyer cost sheet -------------------------------------------------
	def test_buyer_cost_sheet_shows_no_company_figures(self):
		style = self._build("Style Master")
		style.fabric_table[0].db_set({"rate_buyer": 131.25, "total_amt_buyer": 987.65})
		html = frappe.get_print("Style Master", style.name, print_format="Buyer Cost Sheet")
		self.assertIn("131.25", html)
		self.assertIn("987.65", html)
		# our fabric rate and amount from _build, whatever the number format
		self.assertNotIn("120.00", html)
		self.assertNotIn("89,000", html)

	# --- demo data --------------------------------------------------------
	def test_demo_data_installs_and_removes_cleanly(self):
		self.assertEqual(demo.install(), 10)
		self.assertTrue(frappe.db.exists("Merchandiser", "Demo Merchandiser 1"))
		fabric = frappe.db.get_value("Item", {"item_name": "Demo Cotton Poplin"}, "name")
		self.assertTrue(fabric.startswith("F-"), fabric)
		self.assertRaises(frappe.ValidationError, demo.install)

		self.assertEqual(demo.remove(), [])
		self.assertFalse(frappe.db.exists("Item", fabric))
		self.assertFalse(frappe.db.exists("Item Group", "Demo Fabric"))
		self.assertFalse(frappe.db.exists("Merchandiser", "Demo Merchandiser 1"))

	# --- BOM generation ---------------------------------------------------
	def test_boms_are_generated_and_reconcile(self):
		style = self._build("Style Master")
		self.assertRaises(frappe.ValidationError, bom.generate_boms, style.name)

		garment_group = _mk(
			"Item Group",
			item_group_name="SMC Test Garment",
			parent_item_group="All Item Groups",
			is_group=0,
			group_category="Garment",
		)
		garment = frappe.get_doc(
			{
				"doctype": "Item",
				"item_name": f"SMC Garment {style.name}",
				"item_group": garment_group,
				"stock_uom": "Nos",
				"is_stock_item": 0,
				"composition": "100% Cotton",
				"style_master": style.name,
			}
		).insert()

		created = bom.generate_boms(style.name)["created"]
		self.assertEqual(len(created), 1)
		doc = frappe.get_doc("BOM", created[0])
		self.assertEqual((doc.item, doc.docstatus), (garment.name, 0))
		self.assertEqual(
			{row.item_code: row.qty for row in doc.items},
			{self.fabric_item: 1.5, self.trim_item: 8},
		)

		# a second run refreshes the draft instead of adding another BOM
		self.assertEqual(bom.generate_boms(style.name), {"created": [], "updated": created, "skipped": []})

		_columns, data = reconciliation({"style": style.name})
		self.assertEqual({r["status"] for r in data}, {"Match"})

		doc.reload()
		doc.items[0].qty = 1.6
		doc.remove(doc.items[1])
		doc.save()
		_columns, data = reconciliation({"style": style.name, "differences_only": 1})
		self.assertEqual(
			{r["material"]: r["status"] for r in data},
			{self.fabric_item: "Quantity differs", self.trim_item: "Only in costing"},
		)

		doc.submit()
		self.assertEqual(bom.generate_boms(style.name)["skipped"], [garment.name])

	# --- reports ----------------------------------------------------------
	def test_style_costing_summary_report(self):
		style = self._build("Style Master")
		style.db_set("cost_price_our", 400)
		_columns, data = costing_summary({"customer": self.customer})
		row = next(r for r in data if r.name == style.name)
		self.assertEqual((row.margin, row.margin_percent), (100, 20))

	def test_fabric_and_trim_consumption_report(self):
		style = self._build("Style Master")
		_columns, data = consumption({"style": style.name})
		self.assertEqual(
			[(r["material"], r["item"], r["total_req_qty"]) for r in data],
			[("Fabric", self.fabric_item, 1500), ("Trims", self.trim_item, 8000)],
		)
		_columns, data = consumption({"style": style.name, "material": "Trims"})
		self.assertEqual([r["item"] for r in data], [self.trim_item])

	def test_style_order_tracking_report(self):
		style = self._build("Style Master")
		_columns, data = order_tracking({"customer": self.customer})
		row = next(r for r in data if r.name == style.name)
		self.assertEqual((row.status, row.sales_orders), ("Not Ordered", 0))
		_columns, data = order_tracking({"customer": self.customer, "status": "Ordered"})
		self.assertNotIn(style.name, [r.name for r in data])

	def test_role_profiles_pair_app_and_erpnext_roles(self):
		for profile, roles in setup.ROLE_PROFILES.items():
			saved = {r.role for r in frappe.get_doc("Role Profile", profile).roles}
			self.assertEqual(saved, set(roles), profile)

	# --- helpers ----------------------------------------------------------
	def _build(self, doctype):
		return frappe.get_doc(
			{
				"doctype": doctype,
				"style_master_name": f"TEST-{doctype}",
				"customer": self.customer,
				"item": self.product,
				"style_number": "ST-TEST",
				"currency": "INR",
				"garment_qty": 1000,
				"quote_for": "Company",
				"priority": "Medium",
				"sales_price_target": 500,
				"fabric_table": [
					{
						"fabric_name": self.fabric_item,
						"fabric_type": "Local",
						"unit": "Meter",
						"garment_qty": 1000,
						"consumption": 1.5,
						"rate_our": 120,
						"total_req_qty": 1500,
						"amount_our": 180000,
						"gst_percent": 5,
						"total_amt": 189000,
						"per_piece_value": 189,
					}
				],
				"trims_table": [
					{
						"trim_name": self.trim_item,
						"trims_type": "Local",
						"unit": "Nos",
						"trims_qty": 1000,
						"consumption": 8,
						"rate_our": 2,
						"total_req_qty": 8000,
						"amount_our": 16000,
						"gst_percent": 5,
						"total_amt": 16800,
						"per_piece_value": 16.8,
					}
				],
				"manufacturing_cost": [{"cost_head": "CMT", "rate_our": 45, "based_on": "Qty"}],
				"other_cost": [{"cost_head": "COMMISSION", "rate_our": 10}],
				"size": [{"size": "M"}, {"size": "L"}],
			}
		).insert()


def _mk_user(email, role):
	if not frappe.db.exists("User", email):
		user = frappe.get_doc(
			{"doctype": "User", "email": email, "first_name": "SMC Test", "send_welcome_email": 0}
		).insert()
		user.add_roles(role)
	return email


def _item_overrides(*controllers):
	"""Pretend these apps override Item, leaving every other hook alone."""
	get_hooks = frappe.get_hooks

	def fake(hook=None, *args, **kwargs):
		if hook == "override_doctype_class":
			return {"Item": list(controllers)}
		return get_hooks(hook, *args, **kwargs)

	return patch.object(frappe, "get_hooks", side_effect=fake)


def _workflow_doc():
	"""The workflow as it would be created, without touching the site."""
	return {
		"doctype": "Workflow",
		"transitions": [
			{"state": s, "action": a, "next_state": n, "allowed": r} for s, a, n, r in approval.TRANSITIONS
		],
	}


def _set_series(series):
	_set_setting("style_naming_series", series)


def _set_setting(fieldname, value):
	settings = frappe.get_doc("Style Costing Settings")
	settings.set(fieldname, value)
	settings.save()


def _mk(doctype, **kwargs):
	doc = frappe.get_doc({"doctype": doctype, **kwargs})
	doc.insert(ignore_if_duplicate=True)
	return doc.name
