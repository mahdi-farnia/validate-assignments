from pathlib import Path
from typing import AsyncGenerator, override

from aiofiles import open as aioopen
from aiofiles import os as aioos
from src.config import settings
from src.storage.solution import SolutionModel

from .resource import Resource
from .storage import DestinationNotFound, Storage


class DiskStorage(Storage):
    @override
    async def list_sources(
        self,
    ) -> AsyncGenerator[Resource, None]:
        if not await aioos.path.isdir(settings.assets_dir):
            raise DestinationNotFound(f"directory '{settings.assets_dir}' not found")

        for entry in await aioos.scandir(settings.assets_dir):
            if entry.is_file() and entry.name.lower().endswith(
                ".c"
            ):  # currently we are only support c files
                yield Resource(Path(entry.path))

    @override
    async def read_solution(self) -> SolutionModel:
        async with aioopen(settings.solution_json, "r") as f:
            return SolutionModel.model_validate_json(await f.read())

    @override
    async def write_report(self, key: str, content: bytes):
        async with aioopen(Path(settings.assets_dir) / key, "w") as f:
            await f.write(content)  # type: ignore
