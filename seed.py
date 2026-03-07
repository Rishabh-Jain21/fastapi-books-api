from faker import Faker
from database import SessionLocal
import models

fake = Faker()
db = SessionLocal()
books = []

for _ in range(200):
    book = models.Book(
        title=fake.sentence(nb_words=3),
        author=fake.name(),
        year=fake.random_int(min=1950, max=2024)
    )
    books.append(book)

db.add_all(books)
db.commit()

print("Inserted 200 fake books!")