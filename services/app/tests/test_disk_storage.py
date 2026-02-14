import pytest
from src.storage.disk import DiskStorage


class DirEntryMock:
    name: str

    def __init__(self, name: str):
        self.name = name

    def is_file(self):
        return True

    @property
    def path(self):
        return f"/home/sample/{self.name}"


@pytest.mark.asyncio
async def test_disk_listsources(mocker):
    valid_entries = ["123456789.c", "987654321.c"]
    dir_entries = [*valid_entries, "sample.h", "sample.u", "sample.cpp"]
    mocker.patch("aiofiles.os.path.isdir", return_value=True)
    mocker.patch(
        "aiofiles.os.scandir",
        return_value=[DirEntryMock(entry) for entry in dir_entries],
    )
    assert ([p.filename async for p in DiskStorage().list_sources()]) == [
        c[:-2] for c in valid_entries
    ], "C Files Are Not The Only Ones Selected!"
