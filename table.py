from langchain_core.pydantic_v1 import BaseModel, Field

class Table(BaseModel):
    """Table in SQL database."""

    name: str = Field(description="Name of table in SQL database.")
