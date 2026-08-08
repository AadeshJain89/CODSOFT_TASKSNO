# Contact Management System Backend (CodSoft Task 2)

A clean, production-ready RESTful API backend for managing personal and professional contacts securely, built with FastAPI, Async SQLAlchemy, SQLite, Pydantic v2 data validation, duplicate contact prevention, multi-field search, company filtering, sorting, and pagination.

---

## 🚀 Tech Stack

* **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
* **Database ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async with `aiosqlite`)
* **Database**: SQLite
* **Data Validation & Schemas**: [Pydantic v2](https://docs.pydantic.dev/)
* **Authentication**: JWT (`pyjwt`) & Password Hashing (`pwdlib` / `passlib`)
* **Security**: OAuth2 Password Bearer (`/api/users/token`)
* **API Documentation**: Swagger UI (`/docs`) & ReDoc (`/redoc`)

---

## 📁 Project Structure

```
Task_2/
├── routers/
│   ├── __init__.py      # Package marker
│   ├── users.py         # User registration, authentication, & profile endpoints
│   └── contacts.py      # Contact CRUD, search, filtering, sorting, & pagination endpoints
├── main.py              # FastAPI entrypoint, lifespan DB setup, & router registration
├── database.py          # Async SQLAlchemy engine, session maker, & get_db dependency
├── models.py            # User and Contact SQLAlchemy ORM models
├── schemas.py           # Pydantic v2 validation & response schemas
├── auth.py              # Password hashing, JWT token generation, & CurrentUser dependency
├── config.py            # Environment settings via Pydantic BaseSettings
├── requirements.txt     # Dependency specifications
├── .env.example         # Template environment variables
├── .gitignore           # Production gitignore rules
└── README.md            # Project documentation
```

---

## ✨ Key Features

- **🔐 Authentication & User Isolation**: Users can register and log in to get a JWT access token. Every contact is linked to its owner (`user_id`); users cannot view, edit, or delete another user's contacts (`403 Forbidden`).
- **📇 Contact CRUD**:
  - `POST /api/contacts` — Create contact
  - `GET /api/contacts` — List contacts (Search, Filter, Sort, Paginate)
  - `GET /api/contacts/{id}` — Retrieve contact by ID
  - `PUT /api/contacts/{id}` — Full update contact
  - `PATCH /api/contacts/{id}` — Partial update contact
  - `DELETE /api/contacts/{id}` — Delete contact
- **🛡️ Duplicate Prevention**: Prevents creating or updating contacts with duplicate emails or phone numbers within a user's contact list (returns `409 Conflict`).
- **🔍 Multi-Field Search**: Query parameter `search` searches across `first_name`, `last_name`, `email`, `phone_number`, and `company`.
- **🏢 Company Filtering**: Query parameter `company` filters contacts by company.
- **⚡ Sorting & Pagination**:
  - `sort_by`: `first_name`, `last_name`, `company`, or `created_at`
  - `sort_order`: `asc` or `desc`
  - `skip` & `limit` for offset-based pagination.
- **✅ Input Validation**: Validates email format using `EmailStr` and phone numbers using regex pattern validation, returning `422 Unprocessable Entity` for invalid requests.

---

## 🛠️ Setup & Running Instructions

### 1. Clone Repository & Setup Virtual Environment

```bash
cd Task_2
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Setup

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### 4. Run Development Server

```bash
uvicorn main:app --reload
```

- **Base API URL**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

---

## 📊 Database Models

### `User`
* `id` (Integer, Primary Key)
* `username` (String, Unique, Indexed)
* `email` (String, Unique, Indexed)
* `password_hash` (String)
* `created_at` (DateTime, UTC)

### `Contact`
* `id` (Integer, Primary Key)
* `first_name` (String, Indexed)
* `last_name` (String, Optional, Indexed)
* `email` (String, Optional, Indexed)
* `phone_number` (String, Optional, Indexed)
* `address` (Text, Optional)
* `company` (String, Optional, Indexed)
* `user_id` (Integer, ForeignKey to `User.id`)
* `created_at` (DateTime, UTC)
* `updated_at` (DateTime, UTC)

---

## 📡 API Endpoint Reference Table

### Users & Auth (`/api/users`)

| Method | Endpoint | Description | HTTP Status | Auth |
| :--- | :--- | :--- | :---: | :---: |
| `POST` | `/api/users` | Register a new user | `201 Created` | No |
| `POST` | `/api/users/token` | OAuth2 login & return JWT token | `200 OK` | No |
| `GET` | `/api/users/me` | Retrieve profile of authenticated user | `200 OK` | Yes |
| `GET` | `/api/users/{id}` | Get public user info by ID | `200 OK` | No |
| `PATCH` | `/api/users/{id}` | Update current user profile | `200 OK` | Yes |
| `DELETE` | `/api/users/{id}` | Delete current user account | `204 No Content` | Yes |

### Contacts (`/api/contacts`)

| Method | Endpoint | Description | HTTP Status | Auth |
| :--- | :--- | :--- | :---: | :---: |
| `POST` | `/api/contacts` | Create a contact (Checks duplicates) | `201 Created` | Yes |
| `GET` | `/api/contacts` | List contacts (Search, Filter, Sort, Paginate) | `200 OK` | Yes |
| `GET` | `/api/contacts/{id}` | Retrieve single contact by ID | `200 OK` | Yes |
| `PUT` | `/api/contacts/{id}` | Full update contact entry | `200 OK` | Yes |
| `PATCH` | `/api/contacts/{id}` | Partial update contact entry | `200 OK` | Yes |
| `DELETE` | `/api/contacts/{id}` | Delete contact entry | `204 No Content` | Yes |

---

## 💡 Testing via Swagger UI

1. Open `http://127.0.0.1:8000/docs` in your browser.
2. Register a new user at `POST /api/users`.
3. Use `POST /api/users/token` to login and copy the `access_token`.
4. Click **Authorize** at the top right of Swagger, paste the token into the `Value` box, and click **Authorize**.
5. Test all `/api/contacts` endpoints directly from Swagger UI!
