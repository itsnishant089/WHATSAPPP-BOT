from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class IncomingMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    whatsapp_id: str
    phone_number: str | None = None
    profile_name: str | None = None
    message_id: str
    timestamp: str | None = None
    message_type: str = "unknown"
    text: str | None = None
    phone_number_id: str | None = None
    waba_id: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class UserRecord(BaseModel):
    id: str | None = None
    whatsapp_id: str
    phone_number: str | None = None
    profile_name: str | None = None


class UserPreferences(BaseModel):
    whatsapp_user_id: str
    language: str | None = None
    branch: str | None = None
    target_exam: str | None = None
    state: str | None = None
    college: str | None = None
    target_year: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryItem(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class KnowledgeRow(BaseModel):
    source_file: str = ""
    category: str = ""
    subcategory: str = ""
    title: str = ""
    question: str = ""
    answer: str = ""
    keywords: str = ""
    url: str = ""
    branch: str = ""
    exam: str = ""
    priority: int = 0
    active: bool = True
    score: float = 0.0
