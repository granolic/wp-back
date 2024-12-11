from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class InitialAccountState:
    code: Optional[str] = None
    data: Optional[str] = None
