from fastapi import Depends, FastAPI
from database import get_db, Base, engine
from routers import books, reviews, users
from sqlalchemy.orm import Session

app = FastAPI()

app.include_router(books.router)
app.include_router(reviews.router)
app.include_router(users.router)


Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Book Review API running"}


@app.get("/hello")
def say_hello():
    return {"message": "Hello User"}


@app.get("/search")
def search_books(author: str, year: int):
    return {"author": author, "year": year}


@app.get("/db-test")
def db_test(db: Session = Depends(get_db)):
    return {"message": "DB connected"}
