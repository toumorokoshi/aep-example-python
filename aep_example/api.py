from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from .db import get_db, DBShelf, DBBook
from .models import Shelf, Book, ListShelvesResponse, ListBooksResponse

router = APIRouter()

# --- Shelves ---

@router.get("/shelves", response_model=ListShelvesResponse, operation_id="ListShelves", description="List shelves in the library.")
async def list_shelves(
    max_page_size: int = 10,
    page_token: str = "",
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(DBShelf))
    shelves = result.scalars().all()
    # Simple pagination logic omitted for brevity, returning all
    return ListShelvesResponse(shelves=[Shelf(name=s.name, path=s.name, theme=s.theme) for s in shelves])

@router.post("/shelves", response_model=Shelf, status_code=status.HTTP_201_CREATED, operation_id="CreateShelf", description="Create a new shelf.")
async def create_shelf(
    shelf: Shelf,
    id: str = None, # AEP standard query param
    db: AsyncSession = Depends(get_db)
):
    # If shelf_id is provided, construct name, else expect name in body?
    # AEP: Standard Create method takes parent (collection) and the resource body.
    # Resource body likely doesn't have the name populated effectively yet if server assigns.
    # But for client assigned, it might.
    # Here let's assume client provides full name in body for simplicity or we extract ID.

    # Check if exists
    result = await db.execute(select(DBShelf).where(DBShelf.name == shelf.name))
    if result.scalars().first():
         raise HTTPException(status_code=409, detail="Shelf already exists")

    new_shelf = DBShelf(name=shelf.name, theme=shelf.theme)
    db.add(new_shelf)
    await db.commit()
    await db.refresh(new_shelf)
    # Ensure path is set for response
    shelf.path = shelf.name
    return shelf

@router.get("/shelves/{shelf_id}", response_model=Shelf, operation_id="GetShelf", description="Get a shelf by ID.")
async def get_shelf(shelf_id: str, db: AsyncSession = Depends(get_db)):
    name = f"shelves/{shelf_id}"
    result = await db.execute(select(DBShelf).where(DBShelf.name == name))
    shelf = result.scalars().first()
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")
    return Shelf(name=shelf.name, path=shelf.name, theme=shelf.theme)

@router.delete("/shelves/{shelf_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="DeleteShelf", description="Delete a shelf.")
async def delete_shelf(shelf_id: str, db: AsyncSession = Depends(get_db)):
    name = f"shelves/{shelf_id}"
    result = await db.execute(select(DBShelf).where(DBShelf.name == name))
    shelf = result.scalars().first()
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")

    await db.delete(shelf)
    await db.commit()
    return None

# --- Books ---

@router.get("/shelves/{shelf_id}/books", response_model=ListBooksResponse, operation_id="ListBooks", description="List books on a shelf.")
async def list_books(
    shelf_id: str,
    max_page_size: int = 10,
    page_token: str = "",
    db: AsyncSession = Depends(get_db)
):
    shelf_name = f"shelves/{shelf_id}"
    # Verify parent exists
    s_result = await db.execute(select(DBShelf).where(DBShelf.name == shelf_name))
    if not s_result.scalars().first():
         raise HTTPException(status_code=404, detail="Parent shelf not found")

    result = await db.execute(select(DBBook).where(DBBook.shelf_name == shelf_name))
    books = result.scalars().all()
    return ListBooksResponse(books=[Book(name=b.name, path=b.name, title=b.title, author=b.author) for b in books])

@router.post("/shelves/{shelf_id}/books", response_model=Book, status_code=status.HTTP_201_CREATED, operation_id="CreateBook", description="Create a new book on a shelf.")
async def create_book(
    shelf_id: str,
    book: Book,
    id: str = None,
    db: AsyncSession = Depends(get_db)
):
    shelf_name = f"shelves/{shelf_id}"
    # Verify parent exists
    s_result = await db.execute(select(DBShelf).where(DBShelf.name == shelf_name))
    if not s_result.scalars().first():
         raise HTTPException(status_code=404, detail="Parent shelf not found")

    # Verify connection
    if not book.name.startswith(shelf_name + "/books/"):
         raise HTTPException(status_code=400, detail="Book name must start with parent shelf name")

    result = await db.execute(select(DBBook).where(DBBook.name == book.name))
    if result.scalars().first():
         raise HTTPException(status_code=409, detail="Book already exists")

    new_book = DBBook(name=book.name, title=book.title, author=book.author, shelf_name=shelf_name)
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    book.path = book.name
    return book

@router.get("/shelves/{shelf_id}/books/{book_id}", response_model=Book, operation_id="GetBook", description="Get a book by ID.")
async def get_book(shelf_id: str, book_id: str, db: AsyncSession = Depends(get_db)):
    name = f"shelves/{shelf_id}/books/{book_id}"
    result = await db.execute(select(DBBook).where(DBBook.name == name))
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return Book(name=book.name, path=book.name, title=book.title, author=book.author)

@router.delete("/shelves/{shelf_id}/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="DeleteBook", description="Delete a book.")
async def delete_book(shelf_id: str, book_id: str, db: AsyncSession = Depends(get_db)):
    name = f"shelves/{shelf_id}/books/{book_id}"
    result = await db.execute(select(DBBook).where(DBBook.name == name))
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    await db.delete(book)
    await db.commit()
    return None
