from datetime import datetime, timezone
from uuid import uuid4

from evinha.firebase import get_db

EVENTS_COLLECTION = "fundraiser_events"
ORDERS_SUBCOLLECTION = "orders"
PEOPLE_COLLECTION = "people"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _short_id() -> str:
    return uuid4().hex[:12]


# ─── Events ───────────────────────────────────────────────────────────


async def create_event(name: str, date: str, description: str, created_by: str) -> dict:
    db = get_db()
    now = _now()
    doc_ref = db.collection(EVENTS_COLLECTION).document()
    data = {
        "name": name,
        "date": date,
        "description": description,
        "status": "draft",
        "menu_items": [],
        "created_at": now,
        "updated_at": now,
        "created_by": created_by,
    }
    await doc_ref.set(data)
    return {"id": doc_ref.id, **data}


async def list_events(status: str | None = None) -> list[dict]:
    db = get_db()
    query = db.collection(EVENTS_COLLECTION).order_by("date", direction="DESCENDING")
    if status:
        query = query.where("status", "==", status)
    return [{"id": doc.id, **doc.to_dict()} async for doc in query.stream()]


async def get_event(event_id: str) -> dict | None:
    db = get_db()
    doc = await db.collection(EVENTS_COLLECTION).document(event_id).get()
    if not doc.exists:
        return None
    return {"id": doc.id, **doc.to_dict()}


async def update_event(event_id: str, updates: dict) -> dict | None:
    db = get_db()
    ref = db.collection(EVENTS_COLLECTION).document(event_id)
    doc = await ref.get()
    if not doc.exists:
        return None
    updates["updated_at"] = _now()
    await ref.update(updates)
    updated = await ref.get()
    return {"id": updated.id, **updated.to_dict()}


async def replace_menu(event_id: str, menu_items: list[dict]) -> dict | None:
    """Replace the entire menu_items array. Assigns IDs to new items/variants."""
    db = get_db()
    ref = db.collection(EVENTS_COLLECTION).document(event_id)
    doc = await ref.get()
    if not doc.exists:
        return None

    for item in menu_items:
        if not item.get("id"):
            item["id"] = _short_id()
        for variant in item.get("variants", []):
            if not variant.get("id"):
                variant["id"] = _short_id()

    await ref.update({"menu_items": menu_items, "updated_at": _now()})
    updated = await ref.get()
    return {"id": updated.id, **updated.to_dict()}


# ─── People ───────────────────────────────────────────────────────────


async def create_person(name: str, phone: str, notes: str) -> dict:
    db = get_db()
    now = _now()
    doc_ref = db.collection(PEOPLE_COLLECTION).document()
    data = {
        "name": name,
        "phone": phone,
        "notes": notes,
        "created_at": now,
        "updated_at": now,
    }
    await doc_ref.set(data)
    return {"id": doc_ref.id, **data}


async def list_people(query_str: str | None = None) -> list[dict]:
    db = get_db()
    results = []
    async for doc in db.collection(PEOPLE_COLLECTION).stream():
        person = {"id": doc.id, **doc.to_dict()}
        if query_str:
            q = query_str.lower()
            if q not in person.get("name", "").lower() and q not in person.get("phone", ""):
                continue
        results.append(person)
    return results


async def get_person(person_id: str) -> dict | None:
    db = get_db()
    doc = await db.collection(PEOPLE_COLLECTION).document(person_id).get()
    if not doc.exists:
        return None
    return {"id": doc.id, **doc.to_dict()}


async def update_person(person_id: str, updates: dict) -> dict | None:
    db = get_db()
    ref = db.collection(PEOPLE_COLLECTION).document(person_id)
    doc = await ref.get()
    if not doc.exists:
        return None
    updates["updated_at"] = _now()
    await ref.update(updates)
    updated = await ref.get()
    return {"id": updated.id, **updated.to_dict()}


# ─── Orders ───────────────────────────────────────────────────────────


def _orders_ref(event_id: str):
    db = get_db()
    return db.collection(EVENTS_COLLECTION).document(event_id).collection(ORDERS_SUBCOLLECTION)


def _resolve_order_items(items_in: list[dict], menu_items: list[dict]) -> list[dict]:
    """Resolve OrderItemIn dicts to full OrderItem dicts with denormalized name/price."""
    menu_map = {}
    for mi in menu_items:
        for v in mi.get("variants", []):
            menu_map[(mi["id"], v["id"])] = (mi["name"], v["name"], v["price"])

    resolved = []
    for item in items_in:
        key = (item["menu_item_id"], item["variant_id"])
        if key not in menu_map:
            raise ValueError(f"Unknown menu item/variant: {key}")
        mi_name, var_name, price = menu_map[key]
        name = f"{mi_name} — {var_name}" if var_name != "default" else mi_name
        resolved.append({
            "menu_item_id": item["menu_item_id"],
            "variant_id": item["variant_id"],
            "name": name,
            "price": price,
            "quantity": item["quantity"],
        })
    return resolved


def _compute_total(items: list[dict]) -> float:
    return round(sum(i["price"] * i["quantity"] for i in items), 2)


async def create_order(
    event_id: str,
    data: dict,
    menu_items: list[dict],
    created_by: str,
) -> dict:
    items = _resolve_order_items(data.get("items", []), menu_items)
    total = _compute_total(items)
    now = _now()
    order = {
        "person_id": data.get("person_id"),
        "customer_name": data["customer_name"],
        "customer_phone": data.get("customer_phone", ""),
        "order_type": data["order_type"],
        "status": data.get("status", "confirmed"),
        "items": items,
        "total": total,
        "payments": [],
        "amount_paid": 0.0,
        "notes": data.get("notes", ""),
        "created_at": now,
        "updated_at": now,
        "created_by": created_by,
    }
    ref = _orders_ref(event_id).document()
    await ref.set(order)
    return {"id": ref.id, **order}


async def list_orders(
    event_id: str,
    status: str | None = None,
    order_type: str | None = None,
    payment_status: str | None = None,
) -> list[dict]:
    col = _orders_ref(event_id)
    query = col.order_by("created_at", direction="DESCENDING")
    if status:
        query = query.where("status", "==", status)
    if order_type:
        query = query.where("order_type", "==", order_type)

    results = []
    async for doc in query.stream():
        order = {"id": doc.id, **doc.to_dict()}
        if payment_status == "paid" and order["amount_paid"] < order["total"]:
            continue
        if payment_status == "unpaid" and order["amount_paid"] >= order["total"]:
            continue
        results.append(order)
    return results


async def get_order(event_id: str, order_id: str) -> dict | None:
    doc = await _orders_ref(event_id).document(order_id).get()
    if not doc.exists:
        return None
    return {"id": doc.id, **doc.to_dict()}


async def update_order(
    event_id: str,
    order_id: str,
    updates: dict,
    menu_items: list[dict] | None = None,
) -> dict | None:
    ref = _orders_ref(event_id).document(order_id)
    doc = await ref.get()
    if not doc.exists:
        return None

    if "items" in updates and menu_items is not None:
        updates["items"] = _resolve_order_items(updates["items"], menu_items)
        updates["total"] = _compute_total(updates["items"])

    updates["updated_at"] = _now()
    await ref.update(updates)
    updated = await ref.get()
    return {"id": updated.id, **updated.to_dict()}


async def update_order_status(event_id: str, order_id: str, status: str) -> dict | None:
    ref = _orders_ref(event_id).document(order_id)
    doc = await ref.get()
    if not doc.exists:
        return None
    await ref.update({"status": status, "updated_at": _now()})
    updated = await ref.get()
    return {"id": updated.id, **updated.to_dict()}


# ─── Payments ─────────────────────────────────────────────────────────


async def add_payment(
    event_id: str, order_id: str, amount: float, method: str, recorded_by: str
) -> dict | None:
    ref = _orders_ref(event_id).document(order_id)
    doc = await ref.get()
    if not doc.exists:
        return None

    order = doc.to_dict()
    payment = {
        "id": _short_id(),
        "amount": amount,
        "method": method,
        "recorded_at": _now(),
        "recorded_by": recorded_by,
    }
    payments = order.get("payments", []) + [payment]
    amount_paid = round(sum(p["amount"] for p in payments), 2)
    await ref.update({
        "payments": payments,
        "amount_paid": amount_paid,
        "updated_at": _now(),
    })
    updated = await ref.get()
    return {"id": updated.id, **updated.to_dict()}


async def remove_payment(event_id: str, order_id: str, payment_id: str) -> dict | None:
    ref = _orders_ref(event_id).document(order_id)
    doc = await ref.get()
    if not doc.exists:
        return None

    order = doc.to_dict()
    payments = [p for p in order.get("payments", []) if p["id"] != payment_id]
    if len(payments) == len(order.get("payments", [])):
        raise ValueError(f"Payment not found: {payment_id}")

    amount_paid = round(sum(p["amount"] for p in payments), 2)
    await ref.update({
        "payments": payments,
        "amount_paid": amount_paid,
        "updated_at": _now(),
    })
    updated = await ref.get()
    return {"id": updated.id, **updated.to_dict()}


# ─── Summaries ────────────────────────────────────────────────────────


async def get_financial_summary(event_id: str) -> dict:
    orders = await list_orders(event_id)
    total_orders = len(orders)
    total_meals = 0
    total_revenue = 0.0
    total_paid = 0.0
    by_method: dict[str, float] = {}
    by_status: dict[str, int] = {}

    for o in orders:
        total_meals += sum(i["quantity"] for i in o.get("items", []))
        total_revenue += o.get("total", 0)
        total_paid += o.get("amount_paid", 0)
        status = o.get("status", "confirmed")
        by_status[status] = by_status.get(status, 0) + 1
        for p in o.get("payments", []):
            m = p["method"]
            by_method[m] = by_method.get(m, 0) + p["amount"]

    # Round floats
    by_method = {k: round(v, 2) for k, v in by_method.items()}

    return {
        "total_orders": total_orders,
        "total_meals": total_meals,
        "total_revenue": round(total_revenue, 2),
        "total_paid": round(total_paid, 2),
        "total_outstanding": round(total_revenue - total_paid, 2),
        "by_method": by_method,
        "by_status": by_status,
    }


async def get_kitchen_summary(event_id: str) -> list[dict]:
    """Item quantities for the kitchen, only for active orders (confirmed + checked_in)."""
    orders = await list_orders(event_id)
    counts: dict[tuple[str, str], dict] = {}  # (item_name, variant_name) -> {dine_in, to_go}

    for o in orders:
        if o.get("status") not in ("confirmed", "checked_in"):
            continue
        order_type = o.get("order_type", "dine_in")
        for item in o.get("items", []):
            key = (item.get("menu_item_id", ""), item.get("variant_id", ""))
            if key not in counts:
                counts[key] = {
                    "menu_item_name": item["name"].split(" — ")[0] if " — " in item["name"] else item["name"],
                    "variant_name": item["name"].split(" — ")[1] if " — " in item["name"] else "default",
                    "dine_in": 0,
                    "to_go": 0,
                }
            if order_type == "dine_in":
                counts[key]["dine_in"] += item["quantity"]
            else:
                counts[key]["to_go"] += item["quantity"]

    result = []
    for entry in counts.values():
        entry["total"] = entry["dine_in"] + entry["to_go"]
        result.append(entry)
    return result
