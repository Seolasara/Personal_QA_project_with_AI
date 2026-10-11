from pydantic import Field
from schemas.common import StrictModel

class ProductBrandRef(StrictModel):
    id: str
    name: str


class ProductCategoryRef(StrictModel):
    id: str
    name: str
    slug: str


class ProductResponse(StrictModel):
    id: str
    name: str
    description: str
    price: float
    is_location_offer: bool
    is_rental: bool
    co2_rating: str
    in_stock: bool
    is_eco_friendly: bool
    product_image: dict     # Out of Scope: 존재만 확인, 내부 구조는 미검증
    category: ProductCategoryRef
    brand: ProductBrandRef


class ProductDetailCategoryRef(StrictModel):
    id: str
    name: str
    slug: str
    parent_id: str


class ProductSpec(StrictModel):
    id: str
    product_id: str
    spec_name: str
    spec_value: str
    spec_unit: str | None


class ProductDetailResponse(StrictModel):
    id: str
    name: str
    description: str
    price: float
    is_location_offer: bool
    is_rental: bool
    co2_rating: str
    in_stock: bool
    is_eco_friendly: bool
    product_image: dict     # Out of Scope: 존재만 확인, 내부 구조는 미검증
    category: ProductDetailCategoryRef
    brand: ProductBrandRef
    specs: list[ProductSpec]


class RelatedProductCategoryRef(StrictModel):
    id: str
    name: str


class RelatedProductResponse(StrictModel):
    id: str
    name: str
    description: str
    price: float
    is_location_offer: bool
    is_rental: bool
    in_stock: bool
    is_eco_friendly: bool
    product_image: dict     # Out of Scope: 존재만 확인, 내부 구조는 미검증
    category: RelatedProductCategoryRef
    brand: ProductBrandRef


class ProductNotFoundResponse(StrictModel):
    message: str


class PaginatedProductResponse(StrictModel):
    current_page: int
    data: list[ProductResponse]
    from_: int = Field(alias="from")    #파이썬에서는 from_, JSON의 "from" 키와 연결
    last_page: int
    per_page: int
    to: int
    total: int


class SearchProductResponse(StrictModel):
    id: str
    name: str
    description: str
    price: float
    is_location_offer: bool
    is_rental: bool
    co2_rating: str
    in_stock: bool
    is_eco_friendly: bool
    product_image: dict     # Out of Scope: 존재만 확인, 내부 구조는 미검증
    category: RelatedProductCategoryRef
    brand: ProductBrandRef


class PaginatedSearchProductResponse(StrictModel):
    current_page: int
    data: list[SearchProductResponse]
    from_: int | None = Field(alias="from")    # 결과 없으면 null
    last_page: int
    per_page: int
    to: int | None                             # 결과 없으면 null
    total: int
