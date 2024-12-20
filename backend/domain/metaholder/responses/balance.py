from pydantic import BaseModel


class BalanceResponse(BaseModel):
    balance: float
    token_type: str
