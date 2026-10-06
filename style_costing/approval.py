# Copyright (c) 2026, Auriga and contributors
# For license information, please see license.txt
"""The optional costing approval workflow on Style Master.

Draft -> Costed -> Approved -> Quoted. It is created and switched on from
Style Costing Settings rather than shipped as a fixture, because an active
workflow takes over the form's Save and Submit buttons.
"""

import frappe

WORKFLOW = "Style Costing Approval"
MERCHANDISER = "Merchandiser"
COSTING_MANAGER = "Costing Manager"

# (state, docstatus, role allowed to edit in that state)
STATES = (
	("Draft", 0, MERCHANDISER),
	("Draft", 0, COSTING_MANAGER),
	("Costed", 0, COSTING_MANAGER),
	("Approved", 1, COSTING_MANAGER),
	("Quoted", 1, COSTING_MANAGER),
	("Cancelled", 2, COSTING_MANAGER),
)

# (state, action, next state, role allowed to take the action). Everything from
# Approved on changes a submitted document, which only the Costing Manager may.
TRANSITIONS = (
	("Draft", "Mark Costed", "Costed", MERCHANDISER),
	("Draft", "Mark Costed", "Costed", COSTING_MANAGER),
	("Costed", "Send Back", "Draft", COSTING_MANAGER),
	("Costed", "Approve", "Approved", COSTING_MANAGER),
	("Approved", "Mark Quoted", "Quoted", COSTING_MANAGER),
	("Approved", "Cancel", "Cancelled", COSTING_MANAGER),
	("Quoted", "Cancel", "Cancelled", COSTING_MANAGER),
)

STATE_STYLE = {"Costed": "Info", "Approved": "Success", "Quoted": "Primary", "Cancelled": "Danger"}


def sync(enabled: bool):
	"""Create the workflow on first use and switch it on or off."""
	if not frappe.db.exists("Workflow", WORKFLOW):
		if not enabled:
			return
		_create()
		return

	workflow = frappe.get_doc("Workflow", WORKFLOW)
	if bool(workflow.is_active) != bool(enabled):
		workflow.is_active = 1 if enabled else 0
		workflow.save(ignore_permissions=True)


def _create():
	for state in {s[0] for s in STATES}:
		if not frappe.db.exists("Workflow State", state):
			frappe.get_doc(
				{"doctype": "Workflow State", "workflow_state_name": state, "style": STATE_STYLE.get(state, "")}
			).insert(ignore_permissions=True)
	for action in {t[1] for t in TRANSITIONS}:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": action}).insert(
				ignore_permissions=True
			)

	frappe.get_doc(
		{
			"doctype": "Workflow",
			"workflow_name": WORKFLOW,
			"document_type": "Style Master",
			"workflow_state_field": "workflow_state",
			"is_active": 1,
			"send_email_alert": 0,
			"states": [
				{"state": state, "doc_status": str(docstatus), "allow_edit": role}
				for state, docstatus, role in STATES
			],
			"transitions": [
				{"state": state, "action": action, "next_state": next_state, "allowed": role}
				for state, action, next_state, role in TRANSITIONS
			],
		}
	).insert(ignore_permissions=True)
