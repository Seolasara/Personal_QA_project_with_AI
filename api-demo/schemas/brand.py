from schemas.common import StrictModel


class BrandsResponse(StrictModel):
    id: str
    name: str
    slug: str


class BrandNotFoundResponse(StrictModel):
    message: str
