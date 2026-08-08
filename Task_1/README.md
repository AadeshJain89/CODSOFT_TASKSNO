# Student Record Management API (CodSoft Internship Task 1)

A high-performance RESTful Student Record Management API built with **FastAPI**, **SQLAlchemy (Async ORM)**, **SQLite**, and **Pydantic v2**.

---

## 🌟 Key Features

- 🎓 **Student Record Management**: Full CRUD operations for student profiles (`first_name`, `last_name`, `email`, `enrollment_number`, `major`, `gpa`).
- 📚 **Course Management**: Full CRUD operations for courses (`course_code`, `title`, `description`, `credits`, `department`).
- 📝 **Enrollment System**: Associate students with courses, track grades (`grade`) and statuses (`enrolled`, `completed`, `dropped`). Prevent duplicate enrollments via relational foreign key and unique constraints.
- 🔍 **Search, Filtering, Sorting & Pagination**:
  - Filter students by `major` or search across name, email, enrollment number, and major.
  - Filter courses by `department` or search across title, course code, description, and department.
  - Filter enrollments by `student_id`, `course_id`, or `status`.
  - Dynamic sorting (`sort_by`, `order`) and pagination (`skip`, `limit`).
- 🛡️ **Validation & Error Handling**: Comprehensive data validation via Pydantic v2 schemas and clean HTTP status responses (`400`, `404`, `422`).
- 📖 **Interactive API Documentation**: Swagger UI integrated out of the box at `/docs`.

---

## 📁 Project Structure

```text
Task_1/
│
├── main.py            # FastAPI entry point & async lifespan table handler
├── database.py        # Async SQLAlchemy engine & session setup
├── models.py          # SQLAlchemy ORM models (Student, Course, Enrollment)
├── schemas.py         # Pydantic v2 request/response schemas
├── requirements.txt   # Python package dependencies
├── .gitignore         # Git ignore rules
├── test_api.py        # Automated test suite using httpx.AsyncClient
│
└── routers/
    ├── __init__.py    # Routers package initialization
    ├── students.py    # Student CRUD, search, filtering & pagination
    ├── courses.py     # Course CRUD, search, filtering & pagination
    └── enrollments.py # Enrollment CRUD, foreign key checks & duplicate prevention
```

---

## 🗄️ Database Models Schema

### 🎓 Student Model (`students` table)
- `id`: Integer Primary Key, Indexed
- `first_name`: String(50), Not Null
- `last_name`: String(50), Not Null
- `email`: String(120), Unique, Indexed, Not Null
- `enrollment_number`: String(20), Unique, Indexed, Not Null
- `major`: String(50), Indexed, Not Null
- `gpa`: Float, Optional (0.0 to 4.0)
- `created_at`: DateTime (ISO 8601), Auto-generated
- `enrollments`: Relationship with `Enrollment` (cascade delete)

### 📚 Course Model (`courses` table)
- `id`: Integer Primary Key, Indexed
- `course_code`: String(20), Unique, Indexed, Not Null
- `title`: String(100), Not Null
- `description`: Text, Optional
- `credits`: Integer, Not Null (1 to 10)
- `department`: String(50), Indexed, Not Null
- `created_at`: DateTime (ISO 8601), Auto-generated
- `enrollments`: Relationship with `Enrollment` (cascade delete)

### 📝 Enrollment Model (`enrollments` table)
- `id`: Integer Primary Key, Indexed
- `student_id`: Foreign Key (`students.id`), Indexed, Not Null
- `course_id`: Foreign Key (`courses.id`), Indexed, Not Null
- `grade`: String(5), Optional (e.g., `A+`, `A`, `B`, `P`)
- `status`: String(20), Default `enrolled` (`enrolled`, `completed`, `dropped`)
- `enrolled_at`: DateTime (ISO 8601), Auto-generated
- `UniqueConstraint("student_id", "course_id")`: Prevents duplicate student enrollments in the same course

---

## ⚙️ Quick Start Guide

### 1. Set Up Virtual Environment

```bash
cd Task_1

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Automated Test Suite

```bash
python test_api.py
```

### 4. Run the API Server

```bash
uvicorn main:app --reload
```

The API server will start at `http://127.0.0.1:8000`.

---

## 📖 API Documentation & Swagger

Visit **`http://127.0.0.1:8000/docs`** in your browser to test endpoints via Swagger UI.

### 🎓 Student Endpoints

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/students` | Create a new student record | `201 Created` |
| `GET` | `/api/students` | List students (params: `search`, `major`, `sort_by`, `order`, `skip`, `limit`) | `200 OK` |
| `GET` | `/api/students/{id}` | Retrieve student details with enrolled courses | `200 OK` |
| `PUT` | `/api/students/{id}` | Full update of a student record | `200 OK` |
| `PATCH`| `/api/students/{id}` | Partial update of a student record | `200 OK` |
| `DELETE`|`/api/students/{id}`| Delete a student record | `204 No Content` |

### 📚 Course Endpoints

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/courses` | Create a new course | `201 Created` |
| `GET` | `/api/courses` | List courses (params: `search`, `department`, `sort_by`, `order`, `skip`, `limit`) | `200 OK` |
| `GET` | `/api/courses/{id}` | Retrieve course details with enrolled students | `200 OK` |
| `PUT` | `/api/courses/{id}` | Full update of a course | `200 OK` |
| `PATCH`| `/api/courses/{id}` | Partial update of a course | `200 OK` |
| `DELETE`|`/api/courses/{id}`| Delete a course | `204 No Content` |

### 📝 Enrollment Endpoints

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/enrollments` | Enroll a student in a course (prevents duplicate enrollment) | `201 Created` |
| `GET` | `/api/enrollments` | List enrollments (filters: `student_id`, `course_id`, `status`, `skip`, `limit`) | `200 OK` |
| `GET` | `/api/enrollments/{id}` | Retrieve specific enrollment details | `200 OK` |
| `PATCH`| `/api/enrollments/{id}` | Update enrollment grade or status | `200 OK` |
| `DELETE`|`/api/enrollments/{id}`| Drop / delete an enrollment record | `204 No Content` |

---

## 🎬 CodSoft Submission Guidelines

1. **GitHub Repository**: Push this directory as part of your `CODSOFT_TASKSNO` repository.
2. **Video Demo**: Record a short video showcasing:
   - Creating courses and students.
   - Enrolling a student in a course.
   - Demonstrating duplicate enrollment prevention (400 Bad Request).
   - Filtering and searching student/course records in Swagger UI (`http://127.0.0.1:8000/docs`).
   - Updating grade/status and deleting records.
3. **LinkedIn Post**: Share the video on LinkedIn tagging **CodSoft** with hashtags `#codsoft`, `#internship`, `#backend`, `#webdevelopment`, and your GitHub repo link.
