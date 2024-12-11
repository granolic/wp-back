from datetime import datetime

from pydantic import BaseModel


class BetResponse(BaseModel):
    amount: float
    vector: dict
    pair_name: str
    created_at: datetime
