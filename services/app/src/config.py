import sys
import tempfile
from enum import StrEnum
from functools import cached_property
from os import getenv, makedirs
from pathlib import Path

_ASSETS_DIR = getenv("ASSETS")
_APP_NAME = getenv("APP_NAME")
_SOLUTION_JSON = getenv("SOLUTION_JSON")
_RUN_TIMEOUT_SEC = getenv("RUN_TIMEOUT_SEC", "5")
_STORAGE_TYPE = getenv("STORAGE_TYPE")
_S3_ENDPOINT = getenv("S3_ENDPOINT_URL")
_S3_ACCESS_KEY = getenv("S3_ACCESS_KEY")
_S3_SECRET_KEY = getenv("S3_SECRET_KEY")


class StorageType(StrEnum):
    DISK = "disk"
    S3 = "S3"


class Settings:
    @cached_property
    def assets_dir(self) -> str:
        assert _ASSETS_DIR, "ASSERT env not defined!"
        if getenv("STORAGE_TYPE") == StorageType.S3:
            return _ASSETS_DIR

        return Path(_ASSETS_DIR).expanduser().as_posix()

    @cached_property
    def tmpdir(self) -> Path:
        assert _APP_NAME, "APP_NAME env not defined"
        result = Path(tempfile.gettempdir()) / _APP_NAME
        makedirs(result, exist_ok=True)
        return result

    # TODO migrate to S3
    @cached_property
    def solution_json(self) -> str:
        assert _SOLUTION_JSON, "SOLUTION_JSON env not defined!"
        if _STORAGE_TYPE == StorageType.S3:
            return _SOLUTION_JSON
        return Path(_SOLUTION_JSON).expanduser().as_posix()

    @cached_property
    def run_timeout_sec(self) -> int:
        return int(_RUN_TIMEOUT_SEC)

    @cached_property
    def storage_type(self) -> StorageType:
        assert _STORAGE_TYPE, "STORAGE_TYPE is not defined"
        match _STORAGE_TYPE:
            case StorageType.DISK | StorageType.S3 as v:
                return v
            case _:
                raise AssertionError(
                    f"STORAGE_TYPE must be either {StorageType.DISK} or {StorageType.S3}"
                )

    @cached_property
    def s3_endpoint_url(self) -> str:
        if _STORAGE_TYPE == StorageType.S3 and _S3_ENDPOINT is None:
            raise AttributeError(
                "S3_ENDPOINT_URL must be set when source storage set to s3"
            )
        return _STORAGE_TYPE or ""

    @cached_property
    def s3_access_key(self) -> str:
        if _STORAGE_TYPE == StorageType.S3 and _S3_ACCESS_KEY is not None:
            raise AttributeError(
                "S3_ACCESS_KEY must be set when source storage set to s3"
            )
        return _S3_ACCESS_KEY or ""

    @cached_property
    def s3_secret_key(self) -> str:
        if _STORAGE_TYPE == StorageType.S3 and _S3_SECRET_KEY is not None:
            raise AttributeError(
                "S3_SECRET_KEY must be set when source storage set to s3"
            )
        return _S3_SECRET_KEY or ""

    report_md: str = "Report.md"
    report_json: str = "Report.json"


class MockedSettings:
    assets_dir: str = "test"
    tmpdir: Path = Path(f"/tmp/test")
    solution_json: str = "sample.json"
    run_timeout_sec: int = 5
    report_md: str = "Report.md"
    report_json: str = "Report.json"
    storage_type: StorageType = StorageType.DISK
    s3_endpoint_url: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""


settings = Settings() if not "pytest" in sys.modules else MockedSettings()
