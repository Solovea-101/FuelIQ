from pydantic import BaseModel, ConfigDict


class CamelModel(BaseModel):
    """Base model that serializes to camelCase for frontend compatibility."""
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class MessageResponse(CamelModel):
    message: str
