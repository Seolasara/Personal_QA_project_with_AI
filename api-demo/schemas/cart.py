from typing import Any
from schemas.common import StrictModel


class CartCreatedResponse(StrictModel):
    id: str

class CartItemAddedResponse(StrictModel):
    result: str


class CartProductRef(StrictModel):
    id: str
    name: str
    description: str
    price: float
    is_location_offer: bool
    is_rental: bool
    co2_rating: str
    in_stock: bool
    is_eco_friendly: bool

class CartItemsRef(StrictModel):
    id: str
    quantity: int
    discount_percentage: Any = None
    cart_id: str
    product_id: str
    product: CartProductRef

class CartResponse(StrictModel):
    id: str
    additional_discount_percentage: Any = None
    lat: Any = None
    lng: Any = None
    cart_items: list[CartItemsRef]


class UpdatedResponse(StrictModel):
    result: str


class CartMessageResponse(StrictModel):
    message: str


class CartValidationError(StrictModel):
    message: str
    errors: dict[str, list[str]]
