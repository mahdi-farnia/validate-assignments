from contextlib import asynccontextmanager
from typing import Iterator

import pytest
from src.storage.s3 import S3Storage, create_resource


class SessionMock:
    _entries: Iterator[Entry]

    def __init__(self, entries: list[str]):
        self._entries = (self.Entry(e) for e in entries)

    @asynccontextmanager
    async def resource(
        self, type: str, /, aws_access_key_id, aws_secret_access_key, endpoint_url
    ):
        yield self

    async def Bucket(self, assets_dir: str):
        return self

    @property
    def objects(self):
        return self

    async def filter(self):
        for e in self._entries:
            yield e

    class Entry:
        key: str

        def __init__(self, entry: str):
            self.key = entry

        def get(self, what: str):  # what = body
            return self

        async def read(self):
            return ""


@pytest.fixture
def async_open_mocked(mocker):
    class WriterMock:
        async def write(self, b: bytes) -> None: ...

    mocked_open = mocker.AsyncMock()
    mocked_open.__aenter__.return_value = WriterMock()
    yield mocked_open


@pytest.mark.asyncio
async def test_s3_listsource(mocker, async_open_mocked):
    valid_entries = ["123456789.c", "987654321.c"]
    dir_entries = [*valid_entries, "sample.h", "sample.u", "sample.cpp"]
    mocker.patch("aioboto3.Session", return_value=SessionMock(dir_entries))
    mocker.patch("aiofiles.open", return_value=async_open_mocked)
    assert ([p.filename async for p in S3Storage().list_sources()]) == [
        e[:-2] for e in valid_entries
    ], "C Files Are Not The Only Ones Selected!"
