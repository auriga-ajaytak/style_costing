# Style Costing — User Guide

How to set the app up and run a style from enquiry to order. For installation
and the technical notes, see the [README](../README.md).

## 1. Set up

Open the **Styling** workspace. An administrator or Costing Manager does this once.

1. **Style Costing Settings** — choose the style naming series
   (`STY-.YYYY.-.####` by default) and, if you want them, the defaults a new
   style starts from: style rate, efficiency and cost heads. Warnings at the top
   of this page tell you what still needs attention.
2. **Tag your Item Groups.** The Fabric and Trims pickers on a style only list
   items whose Item Group has a **Group Category** of Fabric or Trims. On a site
   with an existing item catalogue, open each fabric, trim and garment group and
   set its category. The settings page shows how many groups are untagged.
3. **Give people roles.** Three role profiles are created at install:

   | Role profile | Can |
   |---|---|
   | Style Merchandiser | Create and edit styles and most masters. Cannot submit a style or delete. |
   | Style Costing Manager | Everything, including submitting, cancelling and amending a style, and the settings. |
   | Style Production Planner | Operation Bulletins and production masters. Reads styles. |

   Each profile also carries the ERPNext roles that person needs for items,
   buyers, quotations and BOMs. Edit them under Role Profile to suit your team.
4. **Demo data** (optional) — *Install Demo Data* on the settings page adds
   sample merchandisers, item groups, items, a buyer and a product. *Remove Demo
   Data* deletes exactly those records, and leaves any that have since been used.

### Item codes

By default every new Item gets a generated code from its Item Group category:
`F-` fabric, `T-` trims, `G-` garment, `Y-` yarn, `CG-` capital goods,
`C-` consumables, `S-` stationery, `I-` otherwise. To type or import your own
codes, tick **Keep ERPNext Item Codes** in the settings.

## 2. Build a style

Create a **Style Master** and work through its tabs.

| Tab | What goes in |
|---|---|
| Style Details | Buyer, style name and number, merchandiser, season, segment, company, currency, size series, garment quantity |
| Techpack | Tech pack attachments |
| BOM | Sales price target, the Fabric and Trims grids and their process routes, and the costing sheet |
| Marker | Design images and the marker table |
| SMV / Production Cost | SMV per production category |
| Value Addition / T&A | Embroidery, print and dye activities; the time and action plan |
| Logistics & Incentive Cost | Incentive rows |
| Instructions | Buyer instructions |
| Sales Price Markup | The markup ladder |
| Lab Test | Lab test templates for the buyer |

The **costing sheet** on the BOM tab is worked out as you enter rows. **Save the
style after editing**: the figures are calculated by the form, so a style
created by data import or API has no costing until it is opened and saved.

## 3. Approve and quote

Without the workflow, a Costing Manager submits the style when the costing is
agreed.

With **Enable Costing Approval Workflow** ticked in the settings, the style
moves through four states and the workflow buttons replace Submit and Cancel:

| From | Action | To | Who |
|---|---|---|---|
| Draft | Mark Costed | Costed | Merchandiser or Costing Manager |
| Costed | Send Back | Draft | Costing Manager |
| Costed | Approve | Approved | Costing Manager |
| Approved | Mark Quoted | Quoted | Costing Manager |
| Approved, Quoted | Cancel | Cancelled | Costing Manager |

Costing Managers get an in-app notification when a style is marked Costed, and
the style's owner gets one when it is approved.

Print **Buyer Cost Sheet** to send the buyer their side of the costing: it
shows the buyer columns only. **Style Costing Sheet** is the internal version.

On a **Quotation**, add styles in the Styles table rather than items.

## 4. From style to order and production

1. **Link the garment Item.** On the garment Item (or each variant of its
   template), set **Style Master** to the style it was costed from. Sales Order
   lines for that item then carry the style automatically.
2. **Create → BOMs** on the style drafts an ERPNext BOM for every linked
   garment Item, from the per-garment consumption of the fabric and trims.
   Review and submit the BOMs in ERPNext. Running it again refreshes the drafts;
   an item that already has a submitted BOM is left alone. Every variant gets
   the same materials.
3. **View → BOM Costing Reconciliation** shows where a BOM has drifted from
   what was quoted.

## 5. Reports

| Report | Answers |
|---|---|
| Style Costing Summary | Cost, target price and margin per style, by buyer, season, segment or merchandiser |
| Fabric and Trim Consumption | What each style consumes, from whom, at what rate |
| BOM Costing Reconciliation | Materials only in the BOM, only in the costing, or with a different quantity |
| Style Order Tracking | Which costed styles became Sales Orders, and for how much |

The Styling workspace also shows counts of styles in progress and submitted,
and charts of styles by buyer, season and merchandiser.

## Good to know

- Style Master and Operation Bulletin keep a version history of every change.
- A warning appears at install, at migrate and on the settings page if another
  installed app also overrides ERPNext's Item — only one app's Item logic runs.
