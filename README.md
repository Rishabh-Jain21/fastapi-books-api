# 📚 FASTAPI-BOOK-API

A production-style REST API for managing books and reviews, built using **FastAPI** and **SQLAlchemy**.

This project demonstrates real-world backend engineering concepts including authentication, authorization, relational data modeling, testing, middleware implementation, and query optimization.

---

## 🚀 Features

* 📘 Full CRUD operations for Books and Reviews
* 🔍 Pagination, filtering, search, and sorting
* 🧹 Soft delete support for Books and Reviews
* 🔐 JWT Authentication (OAuth2 Password Flow)
* 🛡 Role-Based Access Control (RBAC)
* 👤 Ownership-based authorization
* 🔗 One-to-many relationship (Books → Reviews)
* ⭐ Aggregated review statistics (average rating, review count)
* ⚡ Optimized queries using joins and aggregation (avoids N+1 problem)
* 🚦 Token Bucket Rate Limiting Middleware
* 🧪 Automated API testing with Pytest and HTTPX
* 🌱 Seed script using Faker for realistic test data

---

## 🏗 Tech Stack

* **Backend:** FastAPI
* **ORM:** SQLAlchemy (Async)
* **Database:** SQLite (aiosqlite)
* **Authentication:** JWT
* **Validation:** Pydantic
* **Testing:** Pytest, HTTPX
* **Python:** 3.10.11

---

## ⚡ Async Implementation

* AsyncSession for database operations
* Async route handlers
* Async SQLAlchemy queries using `await db.execute()`
* Async integration tests using HTTPX AsyncClient

---

## 🚦 Rate Limiting

The API includes a custom Token Bucket rate limiter implemented as FastAPI middleware.

### Behavior

* Each client IP gets its own token bucket
* Bucket capacity: 10 requests
* Refill rate: 1 token per second
* Requests exceeding the limit receive HTTP 429

### Example Response

```json
{
  "detail": "Too Many Requests"
}
```

### Configuration

Rate limiting can be enabled or disabled using an environment variable:

```env
ENABLE_RATE_LIMITING=true
```

This allows unrestricted access during development while enabling protection in production environments.

---

## 🧪 Testing

The project includes automated tests covering:

### API Tests

* Book CRUD operations
* Review operations
* Authentication flows
* Authorization checks
* Validation scenarios

### Middleware Tests

* Requests under the limit succeed
* Exceeding the limit returns HTTP 429
* Token bucket refills over time
* Independent rate limiting per client

### Test Stack

* Pytest
* HTTPX AsyncClient
* In-memory SQLite database
* Dependency overrides for isolation

Run tests:

```bash
pytest
```

---

## 📡 API Endpoints

### 📚 Books

| Method | Endpoint      | Access                 | Description                                                |
| ------ | ------------- | ---------------------- | ---------------------------------------------------------- |
| GET    | `/books`      | Public / Authenticated | List books with pagination, filtering, search, and sorting |
| GET    | `/books/{id}` | Public / Authenticated | Get book details                                           |
| POST   | `/books`      | Admin Only             | Create a book                                              |
| PUT    | `/books/{id}` | Admin Only             | Update a book                                              |
| PATCH  | `/books/{id}` | Admin Only             | Partial update                                             |
| DELETE | `/books/{id}` | Admin Only             | Soft delete a book                                         |

---

### ⭐ Reviews

| Method | Endpoint              | Access                 | Description   |
| ------ | --------------------- | ---------------------- | ------------- |
| POST   | `/books/{id}/reviews` | Authenticated Users    | Add review    |
| GET    | `/books/{id}/reviews` | Public / Authenticated | List reviews  |
| DELETE | `/reviews/{id}`       | Owner or Admin         | Delete review |

---

### 🔐 Authentication

| Method | Endpoint | Description                        |
| ------ | -------- | ---------------------------------- |
| POST   | `/token` | Login and receive JWT access token |

---

## 📊 Sample Response

### GET `/books`

```json
[
  {
    "id": 1,
    "title": "Atomic Habits",
    "author": "James Clear",
    "review_count": 5,
    "average_rating": 4.6
  }
]
```

### GET `/books/{id}/reviews`

```json
{
  "data": [
    {
      "id": 1,
      "rating": 5,
      "comment": "Great book!",
      "user": {
        "id": 2,
        "username": "john_doe"
      }
    }
  ],
  "meta": {
    "total": 10,
    "page": 1,
    "size": 5
  }
}
```

---

## 🌱 Seed Data

The project includes a Faker-powered seed script.

Generated data:

* 10 Users
* 10 Books
* 25 Reviews
* 1 Admin User

Run:

```bash
python seed.py
```

---

## 🔐 Authorization Model

### Roles

* `user`
* `admin`

### Rules

* Admins can create, update, and delete books
* Users can view books
* Users can create and manage their own reviews
* Admins have full access to all resources

---

## 🧠 Architecture Decisions

### Role-Based Access Control

Book management operations are restricted to administrators to prevent unauthorized modifications.

### Ownership-Based Authorization

Review deletion is restricted to the review owner or an administrator.

### Separate Review Resources

Reviews are exposed through dedicated endpoints to support pagination and scalability.

### Query Optimization

Aggregations use SQL functions such as `COUNT` and `AVG` with `GROUP BY` to avoid N+1 query problems.

### Soft Delete Strategy

Resources are marked as deleted instead of being permanently removed.

### Middleware-Based Rate Limiting

Request throttling is implemented at the middleware layer, keeping rate limiting concerns separate from business logic.

### Environment-Driven Configuration

Application behavior such as rate limiting can be controlled through environment variables without code changes.

---

## 📂 Project Structure

```text
.
├── routers/
│   ├── books.py
│   ├── reviews.py
│   └── users.py
├── tests/
│   ├── conftest.py
│   ├── test_books.py
│   ├── test_sync.py (only for learning purpose to see how to test sync database and sync endpoints)
│   ├── test_reviews.py
│   ├── test_auth.py
│   └── test_middleware.py
├── main.py
├── models.py
├── schemas.py
├── database.py
├── middleware.py
├── auth.py
├── config.py
├── seed.py
├── requirements.txt
├── .env
└── README.md
```

---

## ▶️ Run Locally

This project uses **uv** for dependency and environment management.

```bash
git clone https://github.com/Rishabh-Jain21/FASTAPI-BOOK-API.git

cd FASTAPI-BOOK-API

uv sync
```

Create a `.env` file:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite+aiosqlite:///books.db
ENABLE_RATE_LIMITING=false
```

Start the application:

```bash
uv run uvicorn main:app --reload
```

---

## 🧠 Key Learnings

* Building async APIs with FastAPI and SQLAlchemy
* JWT authentication and authorization
* Role-based and ownership-based access control
* Query optimization using joins and aggregations
* Soft delete implementation
* Middleware development
* Token Bucket rate limiting algorithms
* API testing with Pytest and HTTPX
* Dependency overrides and isolated test databases
* Environment-driven application configuration

---

## 🚀 Future Improvements

* Refresh tokens
* Redis-backed rate limiting
* Dockerization
* CI/CD pipeline
* PostgreSQL support
* API versioning
* OpenTelemetry observability
* Caching layer

---

## ⭐ Support

If you found this project useful, consider giving it a star ⭐
