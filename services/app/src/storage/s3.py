from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, override

import aioboto3
import aiofiles
from src.config import settings
from src.storage.solution import SolutionModel

from .resource import Resource
from .storage import DestinationNotFound, Storage


class S3Storage(Storage):
    _session: aioboto3.Session

    def __init__(self):
        self._session = aioboto3.Session()

    @asynccontextmanager
    async def _resource(self):
        async with self._session.resource(
            "s3",
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            endpoint_url=settings.s3_endpoint_url,
        ) as s3:
            yield s3

    @override
    async def list_sources(
        self,
    ) -> AsyncGenerator[Resource, None]:
        async with self._resource() as s3:
            try:
                bucket = await s3.Bucket(settings.assets_dir)
            except:
                raise DestinationNotFound(f"bucket '{settings.assets_dir}' not exists")

            async for obj in bucket.objects.filter():
                obj_content = await obj.get()
                if obj.key.endswith(".c"):
                    yield await create_resource(
                        obj.key, await obj_content["Body"].read()
                    )

    @override
    async def read_solution(self) -> SolutionModel:
        async with self._resource() as s3:
            solution = Path(settings.solution_json)
            s3_obj = await s3.Object(solution.parts[0], "/".join(solution.parts[1:]))
            s3_obj_content = await s3_obj.get()
            return SolutionModel.model_validate_json(
                await s3_obj_content["Body"].read()
            )

    @override
    async def write_report(self, key: str, content: bytes):
        async with self._resource() as s3:
            s3_obj = await s3.Object(settings.assets_dir, key)
            await s3_obj.put(Body=content)


async def create_resource(key: str, content: bytes) -> Resource:
    dest = settings.tmpdir / key
    async with aiofiles.open(dest, "wb") as f:
        await f.write(content)
    return Resource(dest)
