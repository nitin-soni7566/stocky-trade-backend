from pydantic import BaseModel


class MarginRequest(BaseModel):
    payload: dict
