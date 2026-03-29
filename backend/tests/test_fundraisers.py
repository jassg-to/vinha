"""Tests for the fundraisers API endpoints."""


# ─── Helpers ──────────────────────────────────────────────────────────


SAMPLE_MENU = [
    {
        "name": "Feijoada Tradicional",
        "category": "meal",
        "variants": [
            {"name": "Regular", "price": 25.00},
            {"name": "Pote", "price": 18.00},
        ],
    },
    {
        "name": "Guaraná",
        "category": "drink",
        "variants": [{"name": "default", "price": 2.50}],
    },
]


async def _create_event(client, name="Feijoada de Março"):
    res = await client.post(
        "/api/fundraisers/events",
        json={"name": name, "date": "2026-03-28"},
    )
    assert res.status_code == 200
    return res.json()


async def _set_menu(client, event_id):
    res = await client.put(
        f"/api/fundraisers/events/{event_id}/menu",
        json=SAMPLE_MENU,
    )
    assert res.status_code == 200
    return res.json()


async def _create_order(client, event_id, menu_items, **overrides):
    mi = menu_items[0]
    var = mi["variants"][0]
    order_data = {
        "customer_name": "João Silva",
        "customer_phone": "416-555-1234",
        "order_type": "dine_in",
        "items": [{"menu_item_id": mi["id"], "variant_id": var["id"], "quantity": 2}],
        **overrides,
    }
    res = await client.post(
        f"/api/fundraisers/events/{event_id}/orders",
        json=order_data,
    )
    assert res.status_code == 200
    return res.json()


async def _event_with_menu(manager_client, editor_client):
    """Helper: create event + set menu, return (event, menu_items)."""
    event = await _create_event(manager_client)
    updated = await _set_menu(editor_client, event["id"])
    return updated, updated["menu_items"]


# ─── Event CRUD ───────────────────────────────────────────────────────


async def test_create_event(manager_client):
    event = await _create_event(manager_client)
    assert event["name"] == "Feijoada de Março"
    assert event["status"] == "draft"
    assert event["menu_items"] == []


async def test_create_event_forbidden_for_editor(editor_client):
    res = await editor_client.post(
        "/api/fundraisers/events",
        json={"name": "Test", "date": "2026-01-01"},
    )
    assert res.status_code == 403


async def test_create_event_forbidden_for_no_access(no_access_client):
    res = await no_access_client.post(
        "/api/fundraisers/events",
        json={"name": "Test", "date": "2026-01-01"},
    )
    assert res.status_code == 403


async def test_admin_bypasses_section_check(admin_client):
    event = await _create_event(admin_client)
    assert event["name"] == "Feijoada de Março"


async def test_list_events(manager_client, viewer_client):
    await _create_event(manager_client, "Janeiro")
    await _create_event(manager_client, "Fevereiro")
    res = await viewer_client.get("/api/fundraisers/events")
    assert res.status_code == 200
    assert len(res.json()) == 2


async def test_list_events_filter_by_status(manager_client, viewer_client):
    event = await _create_event(manager_client)
    await manager_client.patch(
        f"/api/fundraisers/events/{event['id']}",
        json={"status": "open"},
    )
    await _create_event(manager_client, "Another")

    res = await viewer_client.get("/api/fundraisers/events?status=open")
    assert len(res.json()) == 1
    assert res.json()[0]["status"] == "open"


async def test_get_event(manager_client, viewer_client):
    event = await _create_event(manager_client)
    res = await viewer_client.get(f"/api/fundraisers/events/{event['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == event["id"]


async def test_get_event_not_found(viewer_client):
    res = await viewer_client.get("/api/fundraisers/events/nonexistent")
    assert res.status_code == 404


async def test_update_event(manager_client):
    event = await _create_event(manager_client)
    res = await manager_client.patch(
        f"/api/fundraisers/events/{event['id']}",
        json={"name": "Feijoada Atualizada", "status": "open"},
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Feijoada Atualizada"
    assert res.json()["status"] == "open"


async def test_update_event_forbidden_for_editor(manager_client, editor_client):
    event = await _create_event(manager_client)
    res = await editor_client.patch(
        f"/api/fundraisers/events/{event['id']}",
        json={"name": "Nope"},
    )
    assert res.status_code == 403


# ─── Menu ─────────────────────────────────────────────────────────────


async def test_replace_menu(manager_client, editor_client):
    event = await _create_event(manager_client)
    updated = await _set_menu(editor_client, event["id"])
    items = updated["menu_items"]
    assert len(items) == 2
    assert items[0]["name"] == "Feijoada Tradicional"
    assert len(items[0]["variants"]) == 2
    assert items[0]["variants"][0]["price"] == 25.00
    assert items[0]["variants"][1]["price"] == 18.00
    assert items[0]["id"]
    assert items[0]["variants"][0]["id"]


async def test_replace_menu_forbidden_for_viewer(manager_client, viewer_client):
    event = await _create_event(manager_client)
    res = await viewer_client.put(
        f"/api/fundraisers/events/{event['id']}/menu",
        json=SAMPLE_MENU,
    )
    assert res.status_code == 403


# ─── People ───────────────────────────────────────────────────────────


async def test_create_and_list_people(editor_client, viewer_client):
    res = await editor_client.post(
        "/api/fundraisers/people",
        json={"name": "Maria Santos", "phone": "416-555-9999"},
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Maria Santos"

    res = await viewer_client.get("/api/fundraisers/people")
    assert len(res.json()) == 1


async def test_search_people(editor_client, viewer_client):
    await editor_client.post(
        "/api/fundraisers/people",
        json={"name": "Maria Santos", "phone": "416-555-9999"},
    )
    await editor_client.post(
        "/api/fundraisers/people",
        json={"name": "João Silva", "phone": "416-555-1111"},
    )

    res = await viewer_client.get("/api/fundraisers/people?q=maria")
    assert len(res.json()) == 1
    assert res.json()[0]["name"] == "Maria Santos"

    res = await viewer_client.get("/api/fundraisers/people?q=416-555-1111")
    assert len(res.json()) == 1
    assert res.json()[0]["name"] == "João Silva"


async def test_update_person(editor_client):
    res = await editor_client.post(
        "/api/fundraisers/people",
        json={"name": "Maria", "phone": "000"},
    )
    person_id = res.json()["id"]
    res = await editor_client.patch(
        f"/api/fundraisers/people/{person_id}",
        json={"phone": "416-555-9999"},
    )
    assert res.status_code == 200
    assert res.json()["phone"] == "416-555-9999"


# ─── Orders ───────────────────────────────────────────────────────────


async def test_create_order(manager_client, editor_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    order = await _create_order(editor_client, event["id"], menu)

    assert order["customer_name"] == "João Silva"
    assert order["status"] == "confirmed"
    assert order["order_type"] == "dine_in"
    assert len(order["items"]) == 1
    assert order["items"][0]["quantity"] == 2
    assert order["items"][0]["price"] == 25.00
    assert order["total"] == 50.00
    assert order["amount_paid"] == 0.0


async def test_create_order_inquiring(manager_client, editor_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    order = await _create_order(
        editor_client, event["id"], menu, status="inquiring", items=[]
    )
    assert order["status"] == "inquiring"
    assert order["items"] == []
    assert order["total"] == 0.0


async def test_create_order_invalid_menu_item(manager_client, editor_client):
    event, _ = await _event_with_menu(manager_client, editor_client)
    res = await editor_client.post(
        f"/api/fundraisers/events/{event['id']}/orders",
        json={
            "customer_name": "Test",
            "order_type": "dine_in",
            "items": [{"menu_item_id": "fake", "variant_id": "fake", "quantity": 1}],
        },
    )
    assert res.status_code == 422


async def test_create_order_forbidden_for_viewer(manager_client, editor_client, viewer_client):
    event, _ = await _event_with_menu(manager_client, editor_client)
    res = await viewer_client.post(
        f"/api/fundraisers/events/{event['id']}/orders",
        json={"customer_name": "Test", "order_type": "dine_in", "items": []},
    )
    assert res.status_code == 403


async def test_list_orders(manager_client, editor_client, viewer_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    await _create_order(editor_client, event["id"], menu)
    await _create_order(
        editor_client, event["id"], menu,
        customer_name="Maria", order_type="to_go",
    )

    res = await viewer_client.get(f"/api/fundraisers/events/{event['id']}/orders")
    assert len(res.json()) == 2


async def test_list_orders_filter_by_type(manager_client, editor_client, viewer_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    await _create_order(editor_client, event["id"], menu, order_type="dine_in")
    await _create_order(editor_client, event["id"], menu, customer_name="B", order_type="to_go")

    res = await viewer_client.get(
        f"/api/fundraisers/events/{event['id']}/orders?order_type=to_go"
    )
    assert len(res.json()) == 1
    assert res.json()[0]["order_type"] == "to_go"


async def test_update_order(manager_client, editor_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    order = await _create_order(editor_client, event["id"], menu)

    res = await editor_client.patch(
        f"/api/fundraisers/events/{event['id']}/orders/{order['id']}",
        json={"notes": "Extra quente"},
    )
    assert res.status_code == 200
    assert res.json()["notes"] == "Extra quente"


async def test_update_order_items(manager_client, editor_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    order = await _create_order(editor_client, event["id"], menu)

    pote_var = menu[0]["variants"][1]
    res = await editor_client.patch(
        f"/api/fundraisers/events/{event['id']}/orders/{order['id']}",
        json={
            "items": [
                {"menu_item_id": menu[0]["id"], "variant_id": pote_var["id"], "quantity": 3}
            ]
        },
    )
    assert res.status_code == 200
    assert res.json()["total"] == 54.00  # 3 * 18


# ─── Order Status ─────────────────────────────────────────────────────


async def test_check_in_order(manager_client, editor_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    order = await _create_order(editor_client, event["id"], menu)

    res = await editor_client.patch(
        f"/api/fundraisers/events/{event['id']}/orders/{order['id']}/status",
        json={"status": "checked_in"},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "checked_in"


async def test_no_show_order(manager_client, editor_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    order = await _create_order(editor_client, event["id"], menu)

    res = await editor_client.patch(
        f"/api/fundraisers/events/{event['id']}/orders/{order['id']}/status",
        json={"status": "no_show"},
    )
    assert res.json()["status"] == "no_show"


async def test_cancel_order(manager_client, editor_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    order = await _create_order(editor_client, event["id"], menu)

    res = await editor_client.patch(
        f"/api/fundraisers/events/{event['id']}/orders/{order['id']}/status",
        json={"status": "cancelled"},
    )
    assert res.json()["status"] == "cancelled"


# ─── Payments ─────────────────────────────────────────────────────────


async def test_add_payment(manager_client, editor_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    order = await _create_order(editor_client, event["id"], menu)

    res = await editor_client.post(
        f"/api/fundraisers/events/{event['id']}/orders/{order['id']}/payments",
        json={"amount": 25.00, "method": "cash"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["amount_paid"] == 25.00
    assert len(data["payments"]) == 1
    assert data["payments"][0]["method"] == "cash"


async def test_multiple_payments(manager_client, editor_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    order = await _create_order(editor_client, event["id"], menu)

    await editor_client.post(
        f"/api/fundraisers/events/{event['id']}/orders/{order['id']}/payments",
        json={"amount": 20.00, "method": "cash"},
    )
    res = await editor_client.post(
        f"/api/fundraisers/events/{event['id']}/orders/{order['id']}/payments",
        json={"amount": 30.00, "method": "square"},
    )
    data = res.json()
    assert data["amount_paid"] == 50.00
    assert len(data["payments"]) == 2


async def test_remove_payment(manager_client, editor_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    order = await _create_order(editor_client, event["id"], menu)

    res = await editor_client.post(
        f"/api/fundraisers/events/{event['id']}/orders/{order['id']}/payments",
        json={"amount": 25.00, "method": "etransfer"},
    )
    payment_id = res.json()["payments"][0]["id"]

    res = await editor_client.delete(
        f"/api/fundraisers/events/{event['id']}/orders/{order['id']}/payments/{payment_id}",
    )
    assert res.status_code == 200
    assert res.json()["amount_paid"] == 0.0
    assert len(res.json()["payments"]) == 0


async def test_remove_nonexistent_payment(manager_client, editor_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    order = await _create_order(editor_client, event["id"], menu)

    res = await editor_client.delete(
        f"/api/fundraisers/events/{event['id']}/orders/{order['id']}/payments/nonexistent",
    )
    assert res.status_code == 404


async def test_list_orders_filter_payment_status(manager_client, editor_client, viewer_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    order1 = await _create_order(editor_client, event["id"], menu, customer_name="Paid")
    await _create_order(editor_client, event["id"], menu, customer_name="Unpaid")

    await editor_client.post(
        f"/api/fundraisers/events/{event['id']}/orders/{order1['id']}/payments",
        json={"amount": 50.00, "method": "cash"},
    )

    res = await viewer_client.get(
        f"/api/fundraisers/events/{event['id']}/orders?payment_status=paid"
    )
    assert len(res.json()) == 1
    assert res.json()[0]["customer_name"] == "Paid"

    res = await viewer_client.get(
        f"/api/fundraisers/events/{event['id']}/orders?payment_status=unpaid"
    )
    assert len(res.json()) == 1
    assert res.json()[0]["customer_name"] == "Unpaid"


# ─── Summaries ────────────────────────────────────────────────────────


async def test_financial_summary(manager_client, editor_client, viewer_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    order1 = await _create_order(editor_client, event["id"], menu)  # 2x $25 = $50
    order2 = await _create_order(
        editor_client, event["id"], menu,
        customer_name="Maria", order_type="to_go",
    )  # 2x $25 = $50

    await editor_client.post(
        f"/api/fundraisers/events/{event['id']}/orders/{order1['id']}/payments",
        json={"amount": 50.00, "method": "cash"},
    )
    await editor_client.post(
        f"/api/fundraisers/events/{event['id']}/orders/{order2['id']}/payments",
        json={"amount": 25.00, "method": "square"},
    )

    res = await viewer_client.get(f"/api/fundraisers/events/{event['id']}/summary")
    assert res.status_code == 200
    summary = res.json()
    assert summary["total_orders"] == 2
    assert summary["total_meals"] == 4
    assert summary["total_revenue"] == 100.00
    assert summary["total_paid"] == 75.00
    assert summary["total_outstanding"] == 25.00
    assert summary["by_method"]["cash"] == 50.00
    assert summary["by_method"]["square"] == 25.00


async def test_kitchen_summary(manager_client, editor_client, viewer_client):
    event, menu = await _event_with_menu(manager_client, editor_client)

    await _create_order(editor_client, event["id"], menu, order_type="dine_in")
    await _create_order(
        editor_client, event["id"], menu,
        customer_name="Maria", order_type="to_go",
    )
    cancelled = await _create_order(
        editor_client, event["id"], menu, customer_name="Cancelled",
    )
    await editor_client.patch(
        f"/api/fundraisers/events/{event['id']}/orders/{cancelled['id']}/status",
        json={"status": "cancelled"},
    )

    res = await viewer_client.get(f"/api/fundraisers/events/{event['id']}/kitchen")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1
    item = items[0]
    assert item["dine_in"] == 2
    assert item["to_go"] == 2
    assert item["total"] == 4


async def test_kitchen_excludes_inquiring(manager_client, editor_client, viewer_client):
    event, menu = await _event_with_menu(manager_client, editor_client)
    await _create_order(editor_client, event["id"], menu, status="inquiring")

    res = await viewer_client.get(f"/api/fundraisers/events/{event['id']}/kitchen")
    assert res.json() == []
