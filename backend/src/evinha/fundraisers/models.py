from pydantic import BaseModel, Field


# --- Menu / Variants ---


class VariantIn(BaseModel):
    name: str
    price: float = Field(ge=0)


class Variant(VariantIn):
    id: str


class MenuItemIn(BaseModel):
    name: str
    category: str = Field(pattern=r"^(meal|drink|dessert|other)$")
    variants: list[VariantIn] = Field(min_length=1)


class MenuItem(BaseModel):
    id: str
    name: str
    category: str
    variants: list[Variant]


# --- Events ---

EVENT_STATUSES = ("draft", "open", "day_of", "closed")


class EventCreate(BaseModel):
    name: str
    date: str  # ISO date YYYY-MM-DD
    description: str = ""


class EventUpdate(BaseModel):
    name: str | None = None
    date: str | None = None
    description: str | None = None
    status: str | None = Field(default=None, pattern=r"^(draft|open|day_of|closed)$")


class Event(BaseModel):
    id: str
    name: str
    date: str
    description: str
    status: str
    menu_items: list[MenuItem]
    created_at: str
    updated_at: str
    created_by: str


# --- People ---


class PersonCreate(BaseModel):
    name: str
    phone: str = ""
    notes: str = ""


class PersonUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    notes: str | None = None


class Person(BaseModel):
    id: str
    name: str
    phone: str
    notes: str
    created_at: str
    updated_at: str


# --- Orders ---

ORDER_STATUSES = ("inquiring", "confirmed", "checked_in", "no_show", "cancelled")


class OrderItemIn(BaseModel):
    menu_item_id: str
    variant_id: str
    quantity: int = Field(ge=1)


class OrderItem(BaseModel):
    menu_item_id: str
    variant_id: str
    name: str  # denormalized: "Item — Variant"
    price: float  # snapshot at order time
    quantity: int


class PaymentIn(BaseModel):
    amount: float = Field(gt=0)
    method: str = Field(pattern=r"^(cash|square|etransfer|donation)$")


class Payment(BaseModel):
    id: str
    amount: float
    method: str
    recorded_at: str
    recorded_by: str


class OrderCreate(BaseModel):
    person_id: str | None = None
    customer_name: str
    customer_phone: str = ""
    order_type: str = Field(pattern=r"^(dine_in|to_go)$")
    status: str = Field(default="confirmed", pattern=r"^(inquiring|confirmed)$")
    items: list[OrderItemIn] = []
    notes: str = ""


class OrderUpdate(BaseModel):
    customer_name: str | None = None
    customer_phone: str | None = None
    order_type: str | None = Field(
        default=None, pattern=r"^(dine_in|to_go)$"
    )
    items: list[OrderItemIn] | None = None
    notes: str | None = None


class StatusUpdate(BaseModel):
    status: str = Field(
        pattern=r"^(inquiring|confirmed|checked_in|no_show|cancelled)$"
    )


class Order(BaseModel):
    id: str
    person_id: str | None
    customer_name: str
    customer_phone: str
    order_type: str
    status: str
    items: list[OrderItem]
    total: float
    payments: list[Payment]
    amount_paid: float
    notes: str
    created_at: str
    updated_at: str
    created_by: str


# --- Summaries ---


class KitchenItem(BaseModel):
    menu_item_name: str
    variant_name: str
    dine_in: int
    to_go: int
    total: int


class FinancialSummary(BaseModel):
    total_orders: int
    total_meals: int  # sum of all item quantities
    total_revenue: float  # sum of all order totals
    total_paid: float
    total_outstanding: float
    by_method: dict[str, float]  # method -> total paid
    by_status: dict[str, int]  # order status -> count
