# Task Tracker Backend (CodSoft Internship Task 3)

A high-performance RESTful Task Management Backend API built with **FastAPI**, **SQLAlchemy (Async ORM)**, **SQLite**, **Pydantic v2**, and **JWT Authentication**.

---

## 🌟 Key Features

- 🔐 **JWT Authentication & Authorization**: Secure registration, login, token verification, and user-isolated task access.
- 📝 **Full Task CRUD**: Create, read, update (PUT/PATCH), and delete tasks.
- 🎯 **Bonus Features**:
  - **Priority Levels**: `low`, `medium`, `high`.
  - **Task Categories**: Filter tasks by category (e.g., `Work`, `Personal`).
  - **Due Dates**: Attach timestamps for task deadlines.
- 🔍 **Filtering & Search**: Filter by completion status (`completed=true/false`), `category`, and search keyword across title, description, or category.
- 📄 **Pagination**: `skip` and `limit` support for large task datasets.
- 📖 **Interactive API Documentation**: Swagger UI integrated out of the box (`/docs`).

---

## 📁 Project Structure

```text
Task_3/
│
├── main.py            # FastAPI entry point & lifespan handler
├── database.py        # Async SQLAlchemy engine & session setup
├── models.py          # SQLAlchemy ORM models (User, Task)
├── schemas.py         # Pydantic v2 request/response schemas
├── auth.py            # Password hashing & JWT dependencies
├── config.py          # Environment settings loader
├── requirements.txt   # Python package dependencies
├── .env.example       # Environment template file
├── .env               # Active environment file (git-ignored)
│
└── routers/
    ├── users.py       # Authentication & profile endpoints
    └── tasks.py       # Task CRUD, filtering & search endpoints
```

---

## 🗄️ Database Models Schema

### 👤 User Model (`users` table)
- `id`: Integer Primary Key
- `username`: String(50), Unique, Not Null
- `email`: String(120), Unique, Not Null
- `password_hash`: String(200), Not Null
- `tasks`: One-to-Many Relationship with `Task`

### 📋 Task Model (`tasks` table)
- `id`: Integer Primary Key
- `title`: String(100), Not Null
- `description`: Text, Not Null
- `completed`: Boolean, Not Null
- `priority`: String(10) (`low`, `medium`, `high`)
- `category`: String(50), Optional (e.g., `Work`, `Personal`)
- `due_date`: DateTime (ISO 8601), Optional
- `created_at`: DateTime (ISO 8601), Auto-generated
- `user_id`: Foreign Key (`users.id`), Index
- `creator`: Many-to-One Relationship with `User`

---

## ⚙️ Quick Start Guide

### 1. Clone & Set Up Virtual Environment

```bash
git clone <your-repo-url>
cd CODSOFT_TASKSNO/Task_3

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration (`.env`)

Copy the `.env.example` template to `.env`:

```bash
cp .env.example .env
```

Ensure `.env` contains your settings:

```env
SECRET_KEY=your_generated_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Run the API Server

```bash
uvicorn main:app --reload
```

The API server will start at `http://127.0.0.1:8000`.

---

## 📖 API Documentation & Swagger

Visit **`http://127.0.0.1:8000/docs`** in your browser to interact with the API endpoints via Swagger UI.

### 🔑 Authentication Endpoints

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/users` | Register a new user account | `201 Created` |
| `POST` | `/api/users/token` | Login to obtain OAuth2 Bearer Access Token | `200 OK` |
| `GET` | `/api/users/me` | Retrieve authenticated user profile | `200 OK` |
| `GET` | `/api/users/{id}` | Get public user profile by ID | `200 OK` |
| `PATCH`| `/api/users/{id}` | Update user profile (self only) | `200 OK` |
| `DELETE`|`/api/users/{id}`| Delete user account (self only) | `204 No Content` |

### 📋 Task Endpoints (Protected - Bearer Token Required)

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/tasks` | Create a new task (with optional `due_date`, `category`, `priority`) | `201 Created` |
| `GET` | `/api/tasks` | List tasks (filters: `completed`, `category`, `search`, `skip`, `limit`) | `200 OK` |
| `GET` | `/api/tasks/{id}` | Retrieve details of a specific task | `200 OK` |
| `PUT` | `/api/tasks/{id}` | Full update of a task | `200 OK` |
| `PATCH`| `/api/tasks/{id}` | Partial update of a task (e.g., mark completed/pending) | `200 OK` |
| `DELETE`|`/api/tasks/{id}`| Delete a task | `204 No Content` |

---

## 🎬 CodSoft Submission Guidelines

1. **GitHub Repository**: Push this directory to your public repository named `CODSOFT_TASKSNO` (or task repo).
2. **Video Demo**: Record a 2–3 minute video showcasing:
   - User registration and login to receive JWT token.
   - Authorizing in Swagger UI (`http://127.0.0.1:8000/docs`).
   - Creating tasks with due dates, priority levels, and categories.
   - Filtering tasks by completion (`completed=true/false`) and category.
   - Updating task completion status and deleting a task.
3. **LinkedIn Post**: Share the video on LinkedIn tagging **CodSoft** with hashtags `#codsoft`, `#internship`, `#backend`, `#webdevelopment`, and your GitHub link.
