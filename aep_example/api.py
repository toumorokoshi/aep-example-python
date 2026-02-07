from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from .db import get_db, DBShelf, DBBook
from .models import Shelf, Book, ListShelvesResponse, ListBooksResponse
import uuid

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
    return ListShelvesResponse(shelves=[Shelf(path=f"shelves/{s.id}", theme=s.theme) for s in shelves])

@router.post("/shelves", response_model=Shelf, status_code=status.HTTP_201_CREATED, operation_id="CreateShelf", description="Create a new shelf.")
async def create_shelf(
    shelf: Shelf,
    id: str = None, # AEP standard query param
    db: AsyncSession = Depends(get_db)
):
    # Construct ID
    if id:
        new_id = id
    else:
        new_id = str(uuid.uuid4())

    # Check if exists
    result = await db.execute(select(DBShelf).where(DBShelf.id == new_id))
    if result.scalars().first():
         raise HTTPException(status_code=409, detail="Shelf already exists")

    new_shelf = DBShelf(id=new_id, theme=shelf.theme)
    db.add(new_shelf)
    await db.commit()
    await db.refresh(new_shelf)

    # Return shelf with populated path
    return Shelf(path=f"shelves/{new_shelf.id}", theme=new_shelf.theme)

@router.get("/shelves/{shelf_id}", response_model=Shelf, operation_id="GetShelf", description="Get a shelf by ID.")
async def get_shelf(shelf_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBShelf).where(DBShelf.id == shelf_id))
    shelf = result.scalars().first()
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")
    return Shelf(path=f"shelves/{shelf.id}", theme=shelf.theme)

@router.delete("/shelves/{shelf_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="DeleteShelf", description="Delete a shelf.")
async def delete_shelf(shelf_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBShelf).where(DBShelf.id == shelf_id))
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
    # Verify parent exists
    s_result = await db.execute(select(DBShelf).where(DBShelf.id == shelf_id))
    if not s_result.scalars().first():
         raise HTTPException(status_code=404, detail="Parent shelf not found")

    result = await db.execute(select(DBBook).where(DBBook.shelf_id == shelf_id))
    books = result.scalars().all()
    return ListBooksResponse(books=[Book(path=f"shelves/{shelf_id}/books/{b.id}", title=b.title, author=b.author) for b in books])

@router.post("/shelves/{shelf_id}/books", response_model=Book, status_code=status.HTTP_201_CREATED, operation_id="CreateBook", description="Create a new book on a shelf.")
async def create_book(
    shelf_id: str,
    book: Book,
    id: str = None,
    db: AsyncSession = Depends(get_db)
):
    # Verify parent exists
    s_result = await db.execute(select(DBShelf).where(DBShelf.id == shelf_id))
    if not s_result.scalars().first():
         raise HTTPException(status_code=404, detail="Parent shelf not found")

    # Construct ID
    if id:
        new_id = id
    else:
        new_id = str(uuid.uuid4())

    result = await db.execute(select(DBBook).where(DBBook.id == new_id))
    if result.scalars().first():
         raise HTTPException(status_code=409, detail="Book already exists")

    new_book = DBBook(id=new_id, title=book.title, author=book.author, shelf_id=shelf_id)
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)

    return Book(path=f"shelves/{shelf_id}/books/{new_book.id}", title=new_book.title, author=new_book.author)

@router.get("/shelves/{shelf_id}/books/{book_id}", response_model=Book, operation_id="GetBook", description="Get a book by ID.")
async def get_book(shelf_id: str, book_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBBook).where(DBBook.id == book_id))
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return Book(path=f"shelves/{shelf_id}/books/{book.id}", title=book.title, author=book.author)

@router.delete("/shelves/{shelf_id}/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="DeleteBook", description="Delete a book.")
async def delete_book(shelf_id: str, book_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBBook).where(DBBook.id == book_id))
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    await db.delete(book)
    await db.commit()
    return None
