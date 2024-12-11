from dataclasses import dataclass

from domain.models.base import BaseModel


@dataclass
class Balance(BaseModel):
    user: 'User'
    balance: float
    token_type: str
