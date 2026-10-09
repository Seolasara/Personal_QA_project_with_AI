from schemas.common import StrictModel
from pydantic import Field


class ProductBrandRef(StrictModel):
    id: str
    name: str


class ProductCategoryRef(StrictModel):
    id: str
    name: str


class ProductResponse(StrictModel):
    id: str
    name: str
    description: str
    price: float
    is_rental: bool
    in_stock: bool
    co2_rating: str
    is_eco_friendly: bool
    brand: ProductBrandRef
    category: ProductCategoryRef
    product_image: dict     # Out of Scope: 존재만 확인, 내부 구조는 미검증



class InvoiceLineResponse(StrictModel):
    id: str
    invoice_id: str
    product_id: str
    unit_price: float
    discount_percentage: int | None
    discounted_price: int | None
    quantity: int
    product: ProductResponse


class Payment(StrictModel):
    payment_method: str
    payment_details: list | None


class InvoiceResponse(StrictModel):
    id: str
    user_id: str
    invoice_date: str
    invoice_number: str
    billing_street: str
    billing_city: str
    billing_country: str
    billing_state: str
    billing_postal_code: str
    additional_discount_percentage: int | None
    additional_discount_amount: int
    subtotal: float
    total: float
    status: str
    status_message: str | None
    invoicelines: list[InvoiceLineResponse]
    created_at: str
    eco_discount_percentage: int
    eco_discount_amount: int
    payment: Payment


# 목록 조회(GET /invoices) 항목은 단건 응답의 축약형이라 별도 모델 (라이브 응답 기준)
class InvoiceListProduct(StrictModel):
    id: str
    name: str
    price: float
    co2_rating: str
    in_stock: bool
    is_eco_friendly: bool
    product_image: dict


class InvoiceListLine(StrictModel):
    id: str
    invoice_id: str
    product_id: str
    unit_price: float
    quantity: int
    discount_percentage: int | None
    discounted_price: int | None
    product: InvoiceListProduct


class InvoiceListPayment(StrictModel):
    payment_method: str


class InvoiceListItem(StrictModel):
    id: str
    user_id: str
    invoice_number: str
    invoice_date: str
    status: str
    total: float
    subtotal: float
    billing_street: str
    billing_city: str
    billing_state: str
    billing_country: str
    billing_postal_code: str
    additional_discount_percentage: int | None
    additional_discount_amount: int
    invoicelines: list[InvoiceListLine]
    payment: InvoiceListPayment


class PaginatedInvoiceResponse(StrictModel):
    current_page: int
    data: list[InvoiceListItem]
    from_: int = Field(alias="from")   #파이썬에서는 from_, JSON의 "from" 키와 연결
    last_page: int
    per_page: int
    to: int
    total: int


class InvoiceCreatedResponse(StrictModel):
    id: str
    user_id: str
    invoice_date: str
    invoice_number: str
    billing_street: str
    billing_city: str
    billing_country: str
    billing_state: str
    billing_postal_code: str
    additional_discount_percentage: int | None
    additional_discount_amount: int
    subtotal: float
    total: float
    created_at: str
    eco_discount_percentage: int
    eco_discount_amount: int
