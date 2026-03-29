from fastapi import APIRouter, Depends, HTTPException

from evinha.auth.dependencies import require_section
from evinha.fundraisers import repository as repo
from evinha.fundraisers.models import (
    Event,
    EventCreate,
    EventUpdate,
    FinancialSummary,
    KitchenItem,
    MenuItemIn,
    Order,
    OrderCreate,
    OrderUpdate,
    PaymentIn,
    Person,
    PersonCreate,
    PersonUpdate,
    StatusUpdate,
)

router = APIRouter(prefix="/fundraisers", tags=["fundraisers"])

_viewer = require_section("fundraisers", "viewer")
_editor = require_section("fundraisers", "editor")
_manager = require_section("fundraisers", "manager")


# ─── Events ───────────────────────────────────────────────────────────


@router.post("/events")
async def post_event(body: EventCreate, caller: dict = Depends(_manager)) -> Event:
    result = await repo.create_event(
        name=body.name,
        date=body.date,
        description=body.description,
        created_by=caller["email"],
    )
    return Event(**result)


@router.get("/events")
async def get_events(
    status: str | None = None, caller: dict = Depends(_viewer)
) -> list[Event]:
    events = await repo.list_events(status=status)
    return [Event(**e) for e in events]


@router.get("/events/{event_id}")
async def get_event(event_id: str, caller: dict = Depends(_viewer)) -> Event:
    event = await repo.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return Event(**event)


@router.patch("/events/{event_id}")
async def patch_event(
    event_id: str, body: EventUpdate, caller: dict = Depends(_manager)
) -> Event:
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await repo.update_event(event_id, updates)
    if not result:
        raise HTTPException(status_code=404, detail="Event not found")
    return Event(**result)


@router.put("/events/{event_id}/menu")
async def put_menu(
    event_id: str,
    body: list[MenuItemIn],
    caller: dict = Depends(_editor),
) -> Event:
    items_dicts = []
    for item in body:
        d = item.model_dump()
        d["id"] = ""  # will be assigned by repo if empty
        for v in d["variants"]:
            v["id"] = ""
        items_dicts.append(d)
    result = await repo.replace_menu(event_id, items_dicts)
    if not result:
        raise HTTPException(status_code=404, detail="Event not found")
    return Event(**result)


# ─── People ───────────────────────────────────────────────────────────


@router.get("/people")
async def get_people(
    q: str | None = None, caller: dict = Depends(_viewer)
) -> list[Person]:
    people = await repo.list_people(query_str=q)
    return [Person(**p) for p in people]


@router.post("/people")
async def post_person(body: PersonCreate, caller: dict = Depends(_editor)) -> Person:
    result = await repo.create_person(
        name=body.name, phone=body.phone, notes=body.notes
    )
    return Person(**result)


@router.patch("/people/{person_id}")
async def patch_person(
    person_id: str, body: PersonUpdate, caller: dict = Depends(_editor)
) -> Person:
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await repo.update_person(person_id, updates)
    if not result:
        raise HTTPException(status_code=404, detail="Person not found")
    return Person(**result)


# ─── Orders ───────────────────────────────────────────────────────────


async def _get_event_or_404(event_id: str) -> dict:
    event = await repo.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/events/{event_id}/orders")
async def post_order(
    event_id: str, body: OrderCreate, caller: dict = Depends(_editor)
) -> Order:
    event = await _get_event_or_404(event_id)
    try:
        result = await repo.create_order(
            event_id=event_id,
            data=body.model_dump(),
            menu_items=event["menu_items"],
            created_by=caller["email"],
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return Order(**result)


@router.get("/events/{event_id}/orders")
async def get_orders(
    event_id: str,
    status: str | None = None,
    order_type: str | None = None,
    payment_status: str | None = None,
    caller: dict = Depends(_viewer),
) -> list[Order]:
    orders = await repo.list_orders(
        event_id, status=status, order_type=order_type, payment_status=payment_status
    )
    return [Order(**o) for o in orders]


@router.get("/events/{event_id}/orders/{order_id}")
async def get_order_detail(
    event_id: str, order_id: str, caller: dict = Depends(_viewer)
) -> Order:
    order = await repo.get_order(event_id, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**order)


@router.patch("/events/{event_id}/orders/{order_id}")
async def patch_order(
    event_id: str,
    order_id: str,
    body: OrderUpdate,
    caller: dict = Depends(_editor),
) -> Order:
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    menu_items = None
    if "items" in updates:
        event = await _get_event_or_404(event_id)
        menu_items = event["menu_items"]
        updates["items"] = [i.model_dump() if hasattr(i, "model_dump") else i for i in updates["items"]]

    try:
        result = await repo.update_order(event_id, order_id, updates, menu_items)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**result)


@router.patch("/events/{event_id}/orders/{order_id}/status")
async def patch_order_status(
    event_id: str,
    order_id: str,
    body: StatusUpdate,
    caller: dict = Depends(_editor),
) -> Order:
    result = await repo.update_order_status(event_id, order_id, body.status)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**result)


# ─── Payments ─────────────────────────────────────────────────────────


@router.post("/events/{event_id}/orders/{order_id}/payments")
async def post_payment(
    event_id: str,
    order_id: str,
    body: PaymentIn,
    caller: dict = Depends(_editor),
) -> Order:
    result = await repo.add_payment(
        event_id, order_id, body.amount, body.method, caller["email"]
    )
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**result)


@router.delete("/events/{event_id}/orders/{order_id}/payments/{payment_id}")
async def delete_payment(
    event_id: str,
    order_id: str,
    payment_id: str,
    caller: dict = Depends(_editor),
) -> Order:
    try:
        result = await repo.remove_payment(event_id, order_id, payment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**result)


# ─── Summaries ────────────────────────────────────────────────────────


@router.get("/events/{event_id}/summary")
async def get_summary(
    event_id: str, caller: dict = Depends(_viewer)
) -> FinancialSummary:
    await _get_event_or_404(event_id)
    data = await repo.get_financial_summary(event_id)
    return FinancialSummary(**data)


@router.get("/events/{event_id}/kitchen")
async def get_kitchen(
    event_id: str, caller: dict = Depends(_viewer)
) -> list[KitchenItem]:
    await _get_event_or_404(event_id)
    items = await repo.get_kitchen_summary(event_id)
    return [KitchenItem(**i) for i in items]
