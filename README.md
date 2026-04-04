# 📚 FASTAPI-BOOK-API

A production-style REST API for managing books and reviews, built using **FastAPI** and **SQLAlchemy**.

This project demonstrates real-world backend engineering concepts including authentication, authorization, relational data modeling, and query optimization.

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
* 🌱 Seed script using Faker for realistic test data

---

## 🏗 Tech Stack

* **Backend:** FastAPI
* **ORM:** SQLAlchemy
* **Database:** SQLite
* **Auth:** JWT
* **Validation:** Pydantic
* **Python:** 3.10.11

---

## 📡 API Endpoints

### 📚 Books

| Method | Endpoint      | Access                 | Description                                         |
| ------ | ------------- | ---------------------- | --------------------------------------------------- |
| GET    | `/books`      | Public / Authenticated | List books (pagination, filtering, search, sorting) |
| GET    | `/books/{id}` | Public / Authenticated | Get book details                                    |
| POST   | `/books`      | Admin only             | Create a book                                       |
| PUT    | `/books/{id}` | Admin only             | Update book                                         |
| PATCH  | `/books/{id}` | Admin only             | Partial update                                      |
| DELETE | `/books/{id}` | Admin only             | Soft delete                                         |

---

### ⭐ Reviews

| Method | Endpoint              | Access                 | Description   |
| ------ | --------------------- | ---------------------- | ------------- |
| POST   | `/books/{id}/reviews` | Authenticated users    | Add review    |
| GET    | `/books/{id}/reviews` | Public / Authenticated | Get reviews   |
| DELETE | `/reviews/{id}`       | Owner or Admin         | Delete review |

---

### 🔐 Authentication

| Method | Endpoint | Description             |
| ------ | -------- | ----------------------- |
| POST   | `/token` | Login and get JWT token |

---

## 📊 Sample Response

### 🔹 GET `/books`

```json id="1q0b5g"
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

---

### 🔹 GET `/books/{id}/reviews`

```json id="9u0rbh"
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

## 🌱 Seed Data (Faker)

The project includes a seed script that uses the **Faker** library to generate realistic test data.

### 📦 Generates:

* 10 Books
* 10 Users *(excluding admin)*
* 25 Reviews across books

### ▶️ Run:

```bash id="n9i2mh"
python seed.py
```

---

## 🔐 Authorization Model

### Roles

* `user`
* `admin`

### Rules

* Only **admins** can create, update, or delete books
* Users can **only view books**
* Users can **create and manage their own reviews**
* Admins have full access

---

## 🧠 Architecture Decisions

### 1. Role-Based Access for Books

* Write operations restricted to admin
* Prevents unauthorized data modification
* Reflects real-world systems (controlled content management)

---

### 2. Separate Review Endpoint

* `/books/{id}/reviews` used instead of embedding
* Supports pagination, filtering, scalability

---

### 3. Aggregation via SQL

* Used `COUNT` and `AVG` with `GROUP BY`
* Avoided hidden ORM computations
* Ensures performance and transparency

---

### 4. Projection Queries

* Selected only required fields
* Reduced payload size and improved performance

---

### 5. Soft Delete Strategy

* Used `is_deleted` flag
* Prevents permanent data loss

---

### 6. Auth vs Authorization Separation

* JWT handles authentication
* RBAC + ownership handle authorization

---

## 📂 Project Structure

Project follows a simple flat structure with minimal folder nesting for ease of learning.

```bash id="dyxfxd"
.
├── routers/           # All API route modules (books, reviews, auth, etc.)
├── main.py            # FastAPI app entry point
├── models.py          # SQLAlchemy models
├── schemas.py         # Pydantic schemas
├── database.py        # DB connection/session
├── auth.py            # Auth, RBAC, utilities
├── seed.py            # Faker-based seed script
├── requirements.txt
├── .env
```

---

## ▶️ Run Locally

```bash id="2n8m4z"
git clone https://github.com/Rishabh-Jain21/FASTAPI-BOOK-API.git
cd FASTAPI-BOOK-API

python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate (Mac/Linux)

pip install -r requirements.txt

# Create .env file
echo SECRET_KEY=your_secret_key > .env

uvicorn main:app --reload
```

---

## 🧠 Key Learnings

* Designed secure APIs with RBAC and ownership checks
* Built efficient queries using aggregation
* Avoided N+1 issues
* Structured scalable endpoints
* Applied clean backend architecture principles

---

## 🚀 Future Improvements

* Refresh tokens
* Redis caching
* Automated tests
* Dockerization
* Deployment

---

## ⭐ Support

If you found this project useful, consider giving it a star ⭐
