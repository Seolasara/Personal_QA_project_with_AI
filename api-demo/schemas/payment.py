from schemas.common import StrictModel

class PaymentResponse(StrictModel):
    message: str


class PaymentValidationError(StrictModel):
    message: str
    errors: dict[str, list[str]]
