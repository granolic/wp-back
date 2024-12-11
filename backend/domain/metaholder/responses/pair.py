from pydantic import BaseModel


class PairResponse(BaseModel):
    name: str
