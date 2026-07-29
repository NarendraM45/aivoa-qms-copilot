from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str

class PaginationParams(BaseModel):
    page: int = 1
    per_page: int = 20
