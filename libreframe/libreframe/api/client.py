"""API Client."""
from datetime import datetime
from pathlib import Path
from random import choice
from tempfile import TemporaryDirectory
from typing import NamedTuple, Optional
from uuid import uuid4

from cached_property import cached_property_with_ttl
from requests import Session

from .schema import APIResponse, Photo


class PhotoResult(NamedTuple):

    photo: Photo
    file: Path

class APIClient:
    """API Client."""

    def __init__(
        self,
        uri: str,
        stream_name: str,
        session: Optional[Session] = None
    ) -> None:
        self._uri = uri
        self._stream_name = stream_name

        if session is None:
            self._session = Session()
        else:
            self._session = session

        self._dir = TemporaryDirectory("libreframe-cache")
        self._dir_path = Path(self._dir.name)

    @cached_property_with_ttl(ttl=30)
    def api_data(self) -> APIResponse:
        return APIResponse(
            stream_name="cat",
            libreframe_version="???",
            photo_period=2,
            photos=[
                Photo(
                    uuid=uuid4(),
                    download_url=f"http://http.cat/{i}.jpg",
                    description=f"HTTP Error {i} but as a cat",
                    location="The Internet",
                    timestamp=datetime.now(),
                    photographer="http.cat",
                ) for i in [100, 101, 102, 200, 201, 202, 204, 206, 207, 300, 301, 302, 303, 304, 305, 307, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417]
            ]
        )

    @property
    def photo_time(self) -> int:
        return self.api_data.photo_period

    def choose_next_photo(self) -> Photo:
        return choice(self.api_data.photos)

    def get_next_photo(self) -> PhotoResult:

        photo = self.choose_next_photo()
        photo_path = self._dir_path.joinpath(str(photo.uuid))

        if not photo_path.exists():
            r = self._session.get(photo.download_url)
            with photo_path.open("wb") as fh:
                # Validate
                fh.write(r.content)

        return PhotoResult(
            photo=photo,
            file=photo_path,
        )

    def __next__(self) -> PhotoResult:
        return self.get_next_photo()

    def __iter__(self) -> 'APIClient':
        return self
