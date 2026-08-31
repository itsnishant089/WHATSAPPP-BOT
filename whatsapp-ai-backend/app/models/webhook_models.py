from typing import Any

from pydantic import BaseModel, ConfigDict


class WebhookEnvelope(BaseModel):
    model_config = ConfigDict(extra="allow")

    object: str | None = None
    entry: list[dict[str, Any]] | None = None
