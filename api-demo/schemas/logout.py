from schemas.common import StrictModel


class LogoutResponse(StrictModel):
    message: str


class LogoutErrorResponse(StrictModel):
    message: str
