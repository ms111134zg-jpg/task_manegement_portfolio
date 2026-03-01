from pydantic import BaseModel, Field

class StatsResponse(BaseModel):
    todo: int
    doing: int
    done: int

