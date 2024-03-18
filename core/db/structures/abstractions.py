from abc import ABC, abstractmethod
from typing import List


class AbstractDBStructure(ABC):
    all_tables: list[str]

    @classmethod
    def get_table_scheme(cls, table_name: str) -> dict:
        if table_name in cls.all_tables:
            return cls._get_structure()[table_name]
        else:
            raise Exception("failed to handle unsupported table")

    @staticmethod
    @abstractmethod
    def _get_structure() -> dict:
        ...
