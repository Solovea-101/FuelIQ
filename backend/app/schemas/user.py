from pydantic import Field

from app.schemas.common import CamelModel


class UserResponse(CamelModel):
    id: str
    email: str
    name: str
    phone: str | None = None
    role: str
    company_id: str = Field(alias="companyId")
    company_name: str = Field(alias="companyName")
    avatar_url: str | None = Field(None, alias="avatarUrl")
    created_at: str = Field(alias="createdAt")
