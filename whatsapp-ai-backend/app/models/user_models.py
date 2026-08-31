from pydantic import BaseModel


class UserUpsert(BaseModel):
    whatsapp_id: str
    phone_number: str | None = None
    profile_name: str | None = None
