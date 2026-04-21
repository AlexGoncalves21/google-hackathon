import uuid
from typing import Literal

from pydantic import BaseModel, Field


class Feedback(BaseModel):
    """Represents user feedback for a conversation."""

    score: int | float
    text: str | None = ""
    log_type: Literal["feedback"] = "feedback"
    service_name: Literal["github-client-agent"] = "github-client-agent"
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
