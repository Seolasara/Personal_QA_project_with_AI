from schemas.common import StrictModel

class LoginResponse(StrictModel):
    access_token: str
    token_type: str
    expires_in: int


class UserAddressRef(StrictModel):
    street: str
    house_number: str | None
    city: str
    state: str | None
    country: str
    postal_code: str | None


class UserResponse(StrictModel):
    first_name: str
    last_name: str
    address: UserAddressRef
    phone: str | None
    dob: str
    email: str
    id: str
    provider: str | None
    totp_enabled: bool
    created_at: str


class LoginErrorResponse(StrictModel):
    error: str
