from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Book Review API running"}


@app.get("/books")
def get_books():
    return ["Book 1", "Book 2"]


@app.get("/hello")
def say_hello():
    return {"message": "Hello User"}
