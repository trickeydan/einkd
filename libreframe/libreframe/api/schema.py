"""API Schema."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class Photo(BaseModel):

    uuid: UUID
    download_url: HttpUrl
    description: Optional[str] = None
    photographer: Optional[str] = None
    location: Optional[str] = None
    timestamp: Optional[datetime] = None


class APIResponse(BaseModel):

    stream_name: str
    libreframe_version: str
    photo_period: int
    photos: List[Photo]