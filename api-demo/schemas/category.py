from typing import Optional
from schemas.common import StrictModel


class CategoryResponse(StrictModel):
    id: str
    parent_id: Optional[str]
    name: str
    slug: str


class CategoryTreeResponse(StrictModel):
    id: str
    parent_id: Optional[str]
    name: str
    slug: str
    sub_categories: list["CategoryTreeResponse"]


class CategoryNotFoundResponse(StrictModel):
    message: str
