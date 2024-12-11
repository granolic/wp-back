from abc import ABC, abstractmethod
from typing import Annotated

from domain.ton import InitialAccountState


class TonClientInterface(ABC):
    @abstractmethod
    async def get_account_address(self, init_state: InitialAccountState) -> Annotated[str, 'Address']:
        ...

    @abstractmethod
    async def get_public_key(self, address: str) -> str:
        ...
