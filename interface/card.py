from typing import Optional
from pydantic import BaseModel

class Card(BaseModel):
    card_number: str
    credit_card_cvv: str
    jwk: object

    def get_card(BaseModel):
        return BaseModel

    class Config:
        arbitrary_types_allowed = True