from schemas.common import StrictModel

class PostcodeResponse(StrictModel):
    street: str
    house_number: str
    city: str
    state: str
    country: str
    postcode: str
    

class PostcodeValidationError(StrictModel):
    message: str
    errors: dict[str, list[str]]
