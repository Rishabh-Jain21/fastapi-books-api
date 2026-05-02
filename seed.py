import random
import asyncio

from faker import Faker
from database import AsyncSessionLocal, engine
import models
from auth import hash_password


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


async def main():

    review_templates: dict[int, list[str]] = {
        1: [
            "This book was very disappointing. The story was confusing and hard to follow.",
            "I couldn't finish this book. The plot felt weak and the characters were boring.",
            "Not worth the time. The writing style made it difficult to stay engaged.",
        ],
        2: [
            "The book had some interesting ideas but overall it was not very engaging.",
            "I expected more from this book. Some parts were okay but many sections dragged.",
            "A few good moments but the story lacked depth.",
        ],
        3: [
            "This was an average read. Some chapters were interesting while others felt slow.",
            "The story was decent but not particularly memorable.",
            "A fairly enjoyable book but it didn't fully capture my attention.",
        ],
        4: [
            "A very enjoyable book with well-developed characters and an engaging plot.",
            "Great storytelling and interesting themes. I would recommend it.",
            "The author did a good job keeping the story engaging throughout.",
        ],
        5: [
            "Absolutely fantastic! The story was captivating from start to finish.",
            "One of the best books I've read recently. Highly recommended.",
            "Brilliant writing and unforgettable characters. Loved every chapter.",
        ],
    }

    fake = Faker()
    db = AsyncSessionLocal()

    # Admin user with username and password "admin"
    admin_user = models.User(
        username="admin",
        email="admin@gmail.com",
        password_hash=hash_password("admin"),
        role="admin",
    )

    users = [admin_user]

    for _ in range(10):
        user = models.User(
            username=fake.user_name(),
            email=fake.unique.email(),
            password_hash=hash_password("abc123"),
        )
        users.append(user)

        db.add_all(users)
        await db.commit()

    books = []

    for _ in range(10):
        book = models.Book(
            title=fake.sentence(nb_words=3),
            author=fake.name(),
            year=fake.random_int(min=1950, max=2024),
        )
        books.append(book)

    db.add_all(books)
    await db.commit()

    print("Inserted 10 fake books!")

    book_reviews = []
    for _ in range(25):
        book_rating = random.randint(1, 5)
        book_review = models.Review(
            book_id=random.randint(1, 10),
            rating=book_rating,
            comment=random.choice(review_templates[book_rating]),
            user_id=random.randint(1, 10),  # Associating comment to a user
        )
        book_reviews.append(book_review)

    db.add_all(book_reviews)
    await db.commit()

    print("Inserted 25 fake book reviews!")


if __name__ == "__main__":
    asyncio.run(create_tables())
    asyncio.run(main())
