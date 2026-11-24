import json
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="FastAPIPractice",
    description="First FastAPI application",
    docs_url="/docs",
    redoc_url="/redoc"
)

DATA_PATH = "src/fastapiprac/data.json"

# Загружаем данные при старте
with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)


# ---------- Модель данных ----------
class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int
    genre: str
    price: float
    in_stock: bool


# Модель для создания/обновления (без id — id назначается сервером при создании)
class BookCreate(BaseModel):
    title: str
    author: str
    year: int
    genre: str
    price: float
    in_stock: bool = True


def save_data():
    """Сохраняет текущее состояние data в файл."""
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------- GET: все книги ----------
@app.get("/books", response_model=list[Book])
async def get_books():
    return data["books"]


# ---------- GET: книга по ID ----------
@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: int):
    for book in data["books"]:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Книга не найдена")


# ---------- POST: добавить книгу ----------
@app.post("/books", response_model=Book, status_code=201)
async def add_book(book: BookCreate):
    new_id = max((b["id"] for b in data["books"]), default=0) + 1
    new_book = {"id": new_id, **book.model_dump()}
    data["books"].append(new_book)
    save_data()
    return new_book


# ---------- PUT: обновить книгу по ID ----------
@app.put("/books/{book_id}", response_model=Book)
async def update_book(book_id: int, book: BookCreate):
    for i, existing in enumerate(data["books"]):
        if existing["id"] == book_id:
            updated = {"id": book_id, **book.model_dump()}
            data["books"][i] = updated
            save_data()
            return updated
    raise HTTPException(status_code=404, detail="Книга не найдена")


# ---------- DELETE: удалить книгу по ID ----------
@app.delete("/books/{book_id}", response_model=Book)
async def delete_book(book_id: int):
    for i, existing in enumerate(data["books"]):
        if existing["id"] == book_id:
            removed = data["books"].pop(i)
            save_data()
            return removed
    raise HTTPException(status_code=404, detail="Книга не найдена")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)