from abc import ABCMeta, abstractmethod
from typing import AsyncGenerator

from .resource import Resource
from .solution import SolutionModel


class Storage(metaclass=ABCMeta):
    @abstractmethod
    def list_sources(self) -> AsyncGenerator[Resource, None]:
        """
        Finding available source files in this storage

        :raise DestinationNotFound:
        """

    @abstractmethod
    async def read_solution(self) -> SolutionModel: ...


class DestinationNotFound(Exception): ...
