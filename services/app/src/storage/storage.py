from abc import ABCMeta, abstractmethod
from typing import AsyncGenerator
from .resource import Resource


class Storage(metaclass=ABCMeta):
    @abstractmethod
    async def list_sources(self) -> AsyncGenerator[Resource, None]:
        """
        Finding available source files in this storage

        :raise DestinationNotFound:
        """


class DestinationNotFound(Exception): ...
