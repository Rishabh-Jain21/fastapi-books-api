from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Book Review API running"}


@app.get("/books")
def get_books():
    return [{"title": "The Hobbit"}, {"title": "Harry Potter"}]


@app.get("/books/{book_id}")
def get_book(book_id: int):
    return {"book_id": book_id}


@app.get("/hello")
def say_hello():
    return {"message": "Hello User"}
