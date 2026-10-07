# Style Costing — User Guide

This guide is for the people who use the app day to day: merchandisers, costing
managers and production planners. It assumes you can log in to ERPNext and
nothing else. For installation, see the [README](../README.md).

**Contents**

1. [What this app is for](#what-this-app-is-for)
2. [Words used in this guide](#words-used-in-this-guide)
3. [Set up (once)](#1-set-up-once)
4. [Cost your first style](#2-cost-your-first-style)
5. [Get the costing approved](#3-get-the-costing-approved)
6. [Quote the buyer](#4-quote-the-buyer)
7. [When the order comes in](#5-when-the-order-comes-in)
8. [Reports](#6-reports)
9. [Common problems](#common-problems)

---

## What this app is for

Before a buyer places an order, you have to tell them a price. To do that you
work out what one garment will cost you: so much fabric, so many buttons and
labels, so many minutes of sewing, plus overheads and commission. Then you add
your margin.

This app is where you do that working-out. You create one **Style Master** for
each garment design, fill in what goes into it, and the app shows you the cost
per piece and the price at different margins. When the buyer agrees, the same
style follows through to the quotation, the sales order and the production BOM.

Everything lives in the **Styling** workspace. Open it from the sidebar.

## Words used in this guide

| Word | Meaning |
|---|---|
| **Style** | One garment design for one buyer, for example "Men's poplin shirt, Buyer X, Summer". |
| **Style Master** | The document that holds everything about a style, including its costing. |
| **Buyer** | Your customer. In ERPNext this is a *Customer*. |
| **Fabric / Trims** | The materials in the garment. Trims are everything that is not fabric: buttons, zips, labels, thread, packaging. |
| **Consumption** | How much of a material one garment uses, for example 1.5 metres of fabric. |
| **SMV** | Standard Minute Value: the minutes of work a garment needs. |
| **Costing sheet** | The summary table that adds everything up to a cost per piece. |
| **Our / Buyer columns** | Most rows have two sets of figures: what it really costs you ("our") and what you show the buyer. |
| **Markup** | The percentage you add on top of cost to reach a selling price. |
| **BOM** | Bill of Materials: the list of materials ERPNext uses to plan production. |
| **Item Group** | ERPNext's folders for items. This app needs to know which folders hold fabric and which hold trims. |

---

## 1. Set up (once)

Someone with the **Costing Manager** or **System Manager** role does this once.
The Styling workspace shows a checklist for the same four steps.

### Step 1 — Open Style Costing Settings

Go to **Styling → Costing → Style Costing Settings**.

If anything still needs attention, an orange message at the top of the page
tells you what. Work through the page from top to bottom:

| Setting | What it does | If unsure |
|---|---|---|
| **Style Naming Series** | The pattern for style numbers. `STY-.YYYY.-.####` gives `STY-2026-0001`. | Leave it. |
| **Enable Costing Approval Workflow** | Makes every style go through Draft → Costed → Approved → Quoted. | Leave it off to begin with. You can turn it on later. |
| **Keep ERPNext Item Codes** | Off: the app gives every new item a code such as `F-0000001`. On: you type or import your own codes. | Leave it off, unless you already have item codes you want to keep. |
| **Default Style Rate / Default Efficiency** | Values filled in for you on new rows. | Leave them blank. |
| **Default Cost Heads** | Cost lines (overhead, commission, ...) added to every new style automatically. | Add the ones you charge on every style. |

Click **Save**.

### Step 2 — Tell the app where your fabric and trims are

**This is the step people miss.** When you add fabric to a style, the app only
offers items from Item Groups marked as *Fabric*. The same goes for trims. If
your groups are not marked, the lists are empty.

1. Go to **Stock → Item Group**.
2. Open each group that holds fabric and set **Group Category** to *Fabric*.
3. Do the same for trims (*Trims*) and for finished garments (*Garment*).
4. Save each one.

Style Costing Settings shows how many groups are still unmarked.

> **What the category also does:** it decides the code of new items in that
> group. Fabric items start with `F-`, trims with `T-`, garments with `G-`,
> yarn `Y-`, capital goods `CG-`, consumables `C-`, stationery `S-`, anything
> else `I-`.

### Step 3 — Give people access

Go to **Users**, open a user, and choose a **Role Profile**:

| Role profile | For | They can |
|---|---|---|
| **Style Merchandiser** | Whoever builds styles and talks to buyers | Create and edit styles and most masters. They cannot submit a style or delete anything. |
| **Style Costing Manager** | Whoever signs off the price | Do everything: approve, submit, cancel and amend styles, and change the settings. |
| **Style Production Planner** | Production planning | Manage operation bulletins and production masters. They can read styles but not change them. |

Each profile already includes the ERPNext access that person needs for items,
buyers, quotations and BOMs.

### Step 4 — Fill in your masters

Under **Styling → Masters** you will find short lists the style form picks
from: Product, Season, Segment, Size Series and others. Seasons,
segments, cost heads, cost types, production processes and value additions
arrive with a few generic entries. Add your own as you need them.

Before your first style you need at least:

- a **Buyer** (ERPNext *Customer*),
- a **Product** (the kind of garment, for example "Men's Shirt"),
- some **fabric and trim items** in tagged Item Groups,
- if you want to record who handles each style, your merchandisers as
  **Employees** in a Department named **Merchandising**.

### Want to try it first? Use the demo data

In Style Costing Settings click **Install Demo Data**. You get three
merchandisers, three tagged item groups, a fabric, a button, a buyer and a
product — enough to build a style straight away.

When you are done, **Remove Demo Data** deletes exactly those records. Anything
you have since used on a real document is kept, and you are told which.

---

## 2. Cost your first style

Go to **Styling → Style Master → Add Style Master**. The form has ten tabs.
You do not need all of them: the first and third are enough for a costing.

### Tab 1 — Style Details

Fill in who and what the style is for.

| Field | What to enter |
|---|---|
| **Buyer** | The customer. |
| **Style Name** *(required)* | The product, for example "Men's Shirt". |
| **Buyer Style Number** *(required)* | The buyer's own reference for the design. |
| **Company** | Your company. Filled in for you. |
| **Merchandiser Code** | Who is handling the style. The list shows **Employees whose Department is named "Merchandising"**, so your merchandisers must be set up as employees in that department. |
| **Season, Segment** | When it is for, and woven or knit. |
| **Currency / Exchange Rate** | The currency you are quoting in. If it is not your company's currency, enter the rate. |
| **Garment Qty** | The quantity you are costing for, for example 1,000 pieces. |
| **Size Series** | The size range, for example S–XL. |

Tick **Is Set**, **Is Panel** or **Is Pack** only if the style is a set of
several garments, is built from panels, or is sold in packs. Extra fields
appear when you do.

### Tab 3 — BOM (where the costing happens)

1. Enter the **Sales Price Target**: the price per piece you are aiming for.
2. In the **Fabric** grid, add a row for each fabric: pick the fabric, enter the
   consumption per garment and the rate. Extras, wastage, freight, duty and tax
   are optional columns on the same row.
3. In the **Trims** grid, do the same for each trim.
4. In **Manufacturing Cost**, add your making costs, for example cutting,
   stitching and finishing.
5. In **Other Cost**, add overheads, commission and similar charges. Your
   default cost heads are already there.

As you type, the **costing sheet** at the bottom updates:

| Line | Meaning |
|---|---|
| Fabric cost (local / import) | Fabric per piece. |
| Trims cost (local / import) | Trims per piece. |
| Manufacturing cost | Making cost per piece. |
| Other cost | Overheads and charges per piece. |
| **Total Cost (A)** | What one piece costs you. |
| **Sales Price Target (B)** | The price you entered. |
| **Difference (B − A)** | Your margin per piece. |
| Incentive (C) | Any export incentive. |
| Difference with incentive | Margin including the incentive. |

Each cost line also shows its share of the total, so you can see at a glance
where the money goes.

### The other tabs

| Tab | Use it for |
|---|---|
| **Techpack** | Attaching the buyer's tech pack files. |
| **Marker** | Design images and marker details (width, efficiency). |
| **SMV / Production Cost** | Sewing minutes per production category. |
| **Value Addition / T&A** | Embroidery, printing or dyeing, and the time-and-action plan. |
| **Logistics & Incentive Cost** | Export incentives. |
| **Instructions** | Notes from the buyer. |
| **Sales Price Markup** | Enter a starting **Markup** % and an **Increment By** %: the table shows the price at five margin levels. |
| **Lab Test** | The lab tests this buyer requires. |

### Save

Click **Save**. The style gets its number, for example `STY-2026-0001`.

> **Always save after changing a style.** The figures are worked out on screen
> as you type and are only stored when you save.

Every change to a style is recorded. Scroll to the bottom of the form to see
who changed what, and when.

---

## 3. Get the costing approved

### If the approval workflow is off

A Costing Manager opens the style and clicks **Submit** when the costing is
agreed. A submitted style can no longer be edited. To change it, the Costing
Manager uses **Cancel** and then **Amend**, which makes a new copy to edit.

### If the approval workflow is on

The style moves through four stages. The button at the top right of the form
shows the next step you are allowed to take.

| Stage | What it means | Next step | Who |
|---|---|---|---|
| **Draft** | Still being worked on. | *Mark Costed* | Merchandiser |
| **Costed** | Ready to be checked. | *Approve*, or *Send Back* to Draft | Costing Manager |
| **Approved** | Price agreed internally. Locked. | *Mark Quoted* | Costing Manager |
| **Quoted** | Sent to the buyer. | *Cancel*, if it must be withdrawn | Costing Manager |

Costing Managers get a notification (the bell at the top of the screen) when a
style is marked Costed. The person who created the style gets one when it is
approved.

---

## 4. Quote the buyer

**Print the cost sheet.** Open the style, click the printer icon, and choose a
format:

| Format | Shows | For |
|---|---|---|
| **Buyer Cost Sheet** | The buyer's figures only. | Sending to the buyer. |
| **Style Costing Sheet** | Your own costs. | Internal use. Do not send this one out. |

**Make a quotation.** Create an ERPNext **Quotation** for the buyer and add your
styles in the **Styles** table. In this app a quotation lists styles, not items.

---

## 5. When the order comes in

### Link the garment item to the style

So that orders can be traced back to the costing, tell ERPNext which item was
costed from which style:

1. Open the garment **Item** (it must be in an Item Group marked *Garment*).
2. Set its **Style Master** field to the style.
3. If the item has sizes or colours as variants, set it on each variant.

From then on, every Sales Order line for that item shows its style.

### Create the production BOMs

On the style, click **Create → BOMs**. The app drafts an ERPNext BOM for every
garment item linked to the style, using the fabric and trims and their
consumption per garment.

- The BOMs are **drafts**. Someone in production reviews and submits them.
- Run it again after changing the style and the drafts are refreshed.
- A BOM that has already been submitted is never touched.
- Extras, wastage and samples are left out: a BOM is what one garment needs.

### Check the BOM still matches what you quoted

On the style, click **View → BOM Costing Reconciliation**. It lists every
material and tells you if it:

- **matches**,
- is **only in the costing** (quoted, but missing from the BOM),
- is **only in the BOM** (being used, but never quoted), or
- has a **different quantity**.

---

## 6. Reports

All four are under **Styling → Reports**.

| Report | Use it to answer |
|---|---|
| **Style Costing Summary** | What does each style cost, what is the target price, and what is the margin? Filter by buyer, season, segment or merchandiser. |
| **Fabric and Trim Consumption** | What materials does a style need, from which supplier, at what rate? |
| **BOM Costing Reconciliation** | Does the production BOM match the costing? |
| **Style Order Tracking** | Which styles turned into orders, and how much was ordered? |

The Styling workspace also shows how many styles are in progress and submitted,
and charts of styles by buyer, season and merchandiser.

---

## Common problems

**The fabric (or trims) list is empty when I add a row.**
The item's Item Group has no Group Category. See
[Step 2](#step-2--tell-the-app-where-your-fabric-and-trims-are).

**I typed an item code and the app changed it.**
The app gives every new item its own code. To keep yours, tick **Keep ERPNext
Item Codes** in Style Costing Settings.

**The Merchandiser list is empty.**
It lists Employees in a Department named "Merchandising". Create that
department and put your merchandisers in it. (The separate *Merchandiser*
master under Masters is not what this field uses.)

**I cannot submit or approve a style.**
Only a Costing Manager can. Ask one, or ask your administrator for the *Style
Costing Manager* role profile.

**The Submit button has gone.**
The approval workflow is on. Use the workflow button at the top right instead.

**A style I imported has no cost.**
Costs are worked out when the style is open on screen. Open it and click Save.

**"Create → BOMs" says no garment item is linked.**
Set the **Style Master** field on the garment item first. See
[Link the garment item](#link-the-garment-item-to-the-style).

**The settings page warns about another app and the Item controller.**
Two installed apps both want to change how items behave, and ERPNext only runs
one. Show the message to your administrator.

**I want to get rid of the demo records.**
Style Costing Settings → **Remove Demo Data**.
