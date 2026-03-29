# Fundraisers

Fundraisers are recurring food events (e.g. monthly feijoada) where people order meals for dine-in or take-out. The system handles the full lifecycle: setting up the event and menu, taking orders, collecting payments, and managing the day-of operations (check-in, kitchen prep, cashier).

## Permissions

Access to fundraisers is controlled by section-based roles. Admins bypass all checks.

| Role | Can do |
|------|--------|
| **Viewer** | See events, orders, and summaries (read-only) |
| **Editor** | Everything a viewer can, plus: create/edit orders, record payments, check people in, edit the menu |
| **Manager** | Everything an editor can, plus: create events, edit event details, change event status |

## Event lifecycle

Each event goes through four statuses:

```
Draft → Open → Day of Event → Closed
```

Managers can advance or revert the status at any time from the event dashboard.

- **Draft** — Setting up the event. Configure the name, date, description, and menu items. Orders can still be created in this phase.
- **Open** — Reservations are open. This is the main phase where orders come in. Kitchen and Cashier views become available.
- **Day of Event** — The event is happening. Staff use the Kitchen view to see what to prepare and the Cashier view to collect payments and check people in.
- **Closed** — Event is over. The dashboard shows the final financial summary.

## Setting up an event

1. Go to **Fundraisers** from the dashboard.
2. Click **New Event**, enter a name and date, then click **Create Event**.
3. You'll land on the **Edit Event** page. Fill in:
   - **Event details** — Name, date, and an optional description.
   - **Menu items** — Each item has a name, a category (Meal, Drink, Dessert, Other), and one or more **variants**. Variants let you offer the same item in different formats at different prices. For example, "Feijoada Tradicional" might have a "Regular" variant at $25 and a "Pote" (container) variant at $18. Items with no meaningful variant use a single "default" variant.
4. Click **Save Menu** to persist the menu.

Editors can update the menu at any time (useful for day-of additions like donated desserts).

## Taking orders

1. From the event dashboard, click **New Order**.
2. **Customer** — Start typing a name. If the person has ordered before, they'll appear in the dropdown (select to auto-fill name and phone). Otherwise, type the name and phone manually; a new person record is created automatically.
3. **Type** — Choose Dine-in or To-go.
4. **Status** — Choose Confirmed (default) or Inquiring. Use Inquiring when a conversation is still ongoing but you want to jot down the details so far.
5. **Items** — Use the +/- buttons to set quantities for each menu item variant. The running total updates live.
6. **Notes** — Optional free-text (e.g. "extra hot", "allergic to peanuts").
7. Click **Save Order**.

### Order statuses

| Status | Meaning |
|--------|---------|
| **Inquiring** | Conversation in progress, details may be incomplete. Not counted in kitchen totals. |
| **Confirmed** | Order is locked in. Counted in kitchen totals. |
| **Checked in** | Customer has arrived at the event. |
| **No show** | Customer did not show up. |
| **Cancelled** | Order was cancelled. |

Status can be changed from the order detail page using the action buttons (Confirm, Check in, No show, Cancel).

## Payments

Payments are recorded from the **order detail page**. The payment section shows:

- The total amount paid so far and the outstanding balance.
- A list of recorded payments with method, amount, who recorded it, and a Remove link.
- A form to add a new payment: enter the amount (pre-filled with the remaining balance) and select a method (Cash, Square, E-transfer, or Donation).

Partial payments are supported — record as many payments as needed until the balance reaches zero.

## Day-of views

These are optimized for phones and tablets used by staff during the event. Both auto-refresh every 30 seconds.

### Kitchen

Shows large cards for each menu item variant with counts split by **Dine-in**, **To-go**, and **Total**. Only counts orders with status Confirmed or Checked in (excludes Inquiring, Cancelled, and No show).

Access: anyone with at least Viewer access.

### Cashier

Shows all active orders (excludes cancelled, no-show, and inquiring) in a card layout. Each card shows:

- Customer name, status badge, order type
- Items summary
- Total, amount paid, and outstanding balance
- **Check in** button (if not yet checked in)
- **Quick-pay buttons** — one-tap buttons for Cash, Square, and E-transfer that pay the full remaining balance in one click. For partial payments or other methods, tap the arrow (→) to go to the full order detail page.

Access: Editors and above.

## Event dashboard

The event dashboard (`/fundraisers/{eventId}`) is the main hub. It shows:

- **Summary cards** — Total orders, total meals, revenue, amount paid, and outstanding balance.
- **Filters** — Filter the order list by status, type (dine-in/to-go), and payment status (paid/unpaid).
- **Order table** — Shows customer name, phone, type, items, total, paid amount, and status. Click any row to open the order detail. On mobile, orders display as cards instead of a table.
- **Action buttons** — Status advance/revert (managers), New Order, Kitchen, Cashier, Edit Event, and Back to events.

## People

The system maintains a simple directory of people (customers) with name and phone. People are created automatically when a new order is placed with an unrecognized name. When creating subsequent orders, typing in the customer field searches existing people for quick selection.

People are shared across all events — a customer who ordered in January will appear in the typeahead when creating a March order.
