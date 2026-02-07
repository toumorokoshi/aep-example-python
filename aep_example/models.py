import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

# Common regex patterns
SHELF_NAME_PATTERN = r"^shelves/[a-zA-Z0-9\-]+$"
BOOK_NAME_PATTERN = r"^shelves/[a-zA-Z0-9\-]+/books/[a-zA-Z0-9\-]+$"

class Shelf(BaseModel):
    path: Optional[str] = Field(default=None, pattern=SHELF_NAME_PATTERN, description="The resource path.", json_schema_extra={"readOnly": True})
    theme: str = Field(description="The theme of the shelf.")

    model_config = {
        "json_schema_extra": {
            "x-aep-resource": {
                "type": "library.example.com/shelf",
                "singular": "shelf",
                "plural": "shelves",
                "patterns": ["shelves/{shelf}"]
            }
        }
    }

class Book(BaseModel):
    path: Optional[str] = Field(default=None, pattern=BOOK_NAME_PATTERN, description="The resource path.", json_schema_extra={"readOnly": True})
    title: str = Field(description="The title of the book.")
    author: str = Field(description="The author of the book.")

    model_config = {
        "json_schema_extra": {
            "x-aep-resource": {
                "type": "library.example.com/book",
                "singular": "book",
                "plural": "books",
                "patterns": ["shelves/{shelf}/books/{book}"]
            }
        }
    }

class ListShelvesResponse(BaseModel):
    shelves: List[Shelf]
    next_page_token: str = ""

class ListBooksResponse(BaseModel):
    books: List[Book]
    next_page_token: str = ""
