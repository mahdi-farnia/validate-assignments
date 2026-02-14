from datetime import timedelta
from os import X_OK
from pathlib import Path
from subprocess import run as run_subprocess, CalledProcessError

from aiofiles import os as aioos
from src.config import settings


class Resource:
    _path: Path

    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def filename(self) -> str:
        return self._path.stem

    async def prepare_resource(self):
        """
        Docstring for prepare_resource

        :raise CompilationError:
        """
        assert self._path.suffix == ".c" and await aioos.path.isfile(
            self._path
        ), "Don't know how to prepare this resource"

        outfile = settings.tmpdir / self._path.stem
        try:
            run_subprocess(
                ["gcc", self._path.as_posix(), "-o", outfile], encoding="utf-8"
            )
        except CalledProcessError as err:
            raise CompilationError(
                f"could not compile {outfile.stem + outfile.suffix}"
            ) from err
        self._path = outfile

    async def run(
        self,
        stdin_lines: list[str],
        timeout: timedelta = timedelta(seconds=settings.run_timeout_sec),
    ) -> list[str]:
        assert await aioos.path.isfile(self._path) and await aioos.access(
            self._path, X_OK, follow_symlinks=False
        ), "Not an executable file"

        try:
            result = run_subprocess(
                [self._path.as_posix()],
                input="\n".join(stdin_lines),
                text=True,
                capture_output=True,
                check=True,
                timeout=timeout.seconds,
            )
        except CalledProcessError as err:
            raise RunError(
                f"'{self._path.stem + self._path.suffix}' exited with status code of none zero"
            ) from err

        return result.stdout.splitlines()


class CompilationError(Exception): ...


class RunError(Exception): ...
