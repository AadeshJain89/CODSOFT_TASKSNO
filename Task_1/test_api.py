import asyncio
import sys
import httpx
from main import app
from database import Base, engine

async def run_tests():
    print("==================================================")
    print("RUNNING STUDENT RECORD MANAGEMENT API TEST SUITE")
    print("==================================================")

    # Initialize database tables for testing
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:


        # ----------------------------------------------------
        # TEST 1: Course Creation
        # ----------------------------------------------------
        print("\n[TEST 1] Course Creation...")
        course_payload = {
            "course_code": "CS101",
            "title": "Introduction to Computer Science",
            "description": "Fundamental concepts of programming and computer science.",
            "credits": 4,
            "department": "Computer Science"
        }
        res = await client.post("/api/courses", json=course_payload)
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
        course1 = res.json()
        assert course1["course_code"] == "CS101"
        assert course1["id"] is not None
        print("  ✓ Course created successfully (ID:", course1["id"], ")")

        # Create second course
        course_payload2 = {
            "course_code": "MATH201",
            "title": "Linear Algebra",
            "description": "Vectors, matrices, and vector spaces.",
            "credits": 3,
            "department": "Mathematics"
        }
        res2 = await client.post("/api/courses", json=course_payload2)
        assert res2.status_code == 201
        course2 = res2.json()
        print("  ✓ Second course created successfully (ID:", course2["id"], ")")

        # Duplicate course code test
        res_dup_course = await client.post("/api/courses", json=course_payload)
        assert res_dup_course.status_code == 400
        print("  ✓ Duplicate course code correctly rejected with 400 Bad Request")

        # ----------------------------------------------------
        # TEST 2: Student Creation
        # ----------------------------------------------------
        print("\n[TEST 2] Student Creation...")
        student_payload = {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@university.edu",
            "enrollment_number": "STU1001",
            "major": "Computer Science",
            "gpa": 3.85
        }
        res = await client.post("/api/students", json=student_payload)
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
        student1 = res.json()
        assert student1["enrollment_number"] == "STU1001"
        assert student1["id"] is not None
        print("  ✓ Student created successfully (ID:", student1["id"], ")")

        # Create second student
        student_payload2 = {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@university.edu",
            "enrollment_number": "STU1002",
            "major": "Mathematics",
            "gpa": 3.40
        }
        res2 = await client.post("/api/students", json=student_payload2)
        assert res2.status_code == 201
        student2 = res2.json()
        print("  ✓ Second student created successfully (ID:", student2["id"], ")")

        # Duplicate student email / enrollment_number test
        res_dup_student = await client.post("/api/students", json=student_payload)
        assert res_dup_student.status_code == 400
        print("  ✓ Duplicate student record correctly rejected with 400 Bad Request")

        # ----------------------------------------------------
        # TEST 3: Student Retrieval, Search, Filter & Pagination
        # ----------------------------------------------------
        print("\n[TEST 3] Student Retrieval, Search, Filter, Sort & Pagination...")
        # Get all students
        res = await client.get("/api/students")
        assert res.status_code == 200
        students_list = res.json()
        assert len(students_list) == 2
        print("  ✓ List all students returned", len(students_list), "records")

        # Filter by major
        res = await client.get("/api/students?major=Computer Science")
        assert res.status_code == 200
        assert len(res.json()) == 1
        assert res.json()[0]["first_name"] == "Alice"
        print("  ✓ Major filter returned correct record")

        # Search keyword
        res = await client.get("/api/students?search=Johnson")
        assert res.status_code == 200
        assert len(res.json()) == 1
        assert res.json()[0]["last_name"] == "Johnson"
        print("  ✓ Search query returned correct record")

        # Sorting & Pagination
        res = await client.get("/api/students?sort_by=gpa&order=desc&skip=0&limit=1")
        assert res.status_code == 200
        assert len(res.json()) == 1
        assert res.json()[0]["first_name"] == "Alice"
        print("  ✓ Sorting & pagination parameters working as expected")

        # Retrieve student by ID
        res = await client.get(f"/api/students/{student1['id']}")
        assert res.status_code == 200
        assert res.json()["first_name"] == "Alice"
        print("  ✓ Student by ID retrieved successfully")

        # ----------------------------------------------------
        # TEST 4: Student Update (PUT & PATCH)
        # ----------------------------------------------------
        print("\n[TEST 4] Student Update (PUT & PATCH)...")
        # PATCH update GPA
        res = await client.patch(f"/api/students/{student1['id']}", json={"gpa": 3.95})
        assert res.status_code == 200
        assert res.json()["gpa"] == 3.95
        print("  ✓ PATCH updated student GPA to 3.95")

        # PUT full update
        updated_payload = {
            "first_name": "Alice",
            "last_name": "Smith-Doe",
            "email": "alice.smith@university.edu",
            "enrollment_number": "STU1001",
            "major": "Data Science",
            "gpa": 3.95
        }
        res = await client.put(f"/api/students/{student1['id']}", json=updated_payload)
        assert res.status_code == 200
        assert res.json()["last_name"] == "Smith-Doe"
        assert res.json()["major"] == "Data Science"
        print("  ✓ PUT updated student record successfully")

        # ----------------------------------------------------
        # TEST 5: Enrollment Creation & Prevention of Duplicates
        # ----------------------------------------------------
        print("\n[TEST 5] Enrollment Creation & Duplicate Prevention...")
        enrollment_payload = {
            "student_id": student1["id"],
            "course_id": course1["id"],
            "grade": "A",
            "status": "enrolled"
        }
        res = await client.post("/api/enrollments", json=enrollment_payload)
        assert res.status_code == 201
        enrollment1 = res.json()
        assert enrollment1["student_id"] == student1["id"]
        assert enrollment1["course_id"] == course1["id"]
        print("  ✓ Enrollment created successfully (ID:", enrollment1["id"], ")")

        # Attempt duplicate enrollment
        res_dup_enr = await client.post("/api/enrollments", json=enrollment_payload)
        assert res_dup_enr.status_code == 400
        assert "already enrolled" in res_dup_enr.json()["detail"]
        print("  ✓ Duplicate enrollment prevented with 400 Bad Request")

        # Enroll student 2 in course 1
        res = await client.post("/api/enrollments", json={
            "student_id": student2["id"],
            "course_id": course1["id"],
            "status": "enrolled"
        })
        assert res.status_code == 201
        print("  ✓ Student 2 enrolled in course 1 successfully")

        # ----------------------------------------------------
        # TEST 6: Invalid Foreign Key Handling
        # ----------------------------------------------------
        print("\n[TEST 6] Invalid Foreign Key Handling...")
        # Invalid student ID
        res = await client.post("/api/enrollments", json={
            "student_id": 9999,
            "course_id": course1["id"],
            "status": "enrolled"
        })
        assert res.status_code == 404
        assert "Student with ID 9999 not found" in res.json()["detail"]
        print("  ✓ Invalid student ID returns 404 Not Found")

        # Invalid course ID
        res = await client.post("/api/enrollments", json={
            "student_id": student1["id"],
            "course_id": 9999,
            "status": "enrolled"
        })
        assert res.status_code == 404
        assert "Course with ID 9999 not found" in res.json()["detail"]
        print("  ✓ Invalid course ID returns 404 Not Found")

        # ----------------------------------------------------
        # TEST 7: Enrollment Retrieval & Filtering
        # ----------------------------------------------------
        print("\n[TEST 7] Enrollment Retrieval & Filtering...")
        res = await client.get(f"/api/enrollments?student_id={student1['id']}")
        assert res.status_code == 200
        assert len(res.json()) == 1
        print("  ✓ Enrollments filtered by student ID successfully")

        # Verify Student Detail contains nested enrolled course
        res = await client.get(f"/api/students/{student1['id']}")
        assert res.status_code == 200
        student_detail = res.json()
        assert len(student_detail["enrollments"]) == 1
        assert student_detail["enrollments"][0]["course"]["course_code"] == "CS101"
        print("  ✓ Student detail eagerly populated enrolled course CS101")

        # Verify Course Detail contains nested enrolled student
        res = await client.get(f"/api/courses/{course1['id']}")
        assert res.status_code == 200
        course_detail = res.json()
        assert len(course_detail["enrollments"]) == 2
        print("  ✓ Course detail eagerly populated 2 enrolled students")

        # ----------------------------------------------------
        # TEST 8: Enrollment Update & Deletion
        # ----------------------------------------------------
        print("\n[TEST 8] Enrollment Update & Deletion...")
        res = await client.patch(f"/api/enrollments/{enrollment1['id']}", json={
            "grade": "A+",
            "status": "completed"
        })
        assert res.status_code == 200
        assert res.json()["grade"] == "A+"
        assert res.json()["status"] == "completed"
        print("  ✓ Enrollment status and grade updated to completed / A+")

        # Delete enrollment
        res = await client.delete(f"/api/enrollments/{enrollment1['id']}")
        assert res.status_code == 204
        print("  ✓ Enrollment deleted successfully")

        # Verify deletion
        res = await client.get(f"/api/enrollments/{enrollment1['id']}")
        assert res.status_code == 404
        print("  ✓ Enrollment deletion verified (404 Not Found)")

        # ----------------------------------------------------
        # TEST 9: Student & Course Deletion
        # ----------------------------------------------------
        print("\n[TEST 9] Student & Course Deletion...")
        res = await client.delete(f"/api/students/{student2['id']}")
        assert res.status_code == 204
        print("  ✓ Student 2 deleted successfully")

        res = await client.delete(f"/api/courses/{course2['id']}")
        assert res.status_code == 204
        print("  ✓ Course 2 deleted successfully")

        # ----------------------------------------------------
        # TEST 10: Validation Error Verification
        # ----------------------------------------------------
        print("\n[TEST 10] Pydantic Validation Errors...")
        # Invalid email
        res = await client.post("/api/students", json={
            "first_name": "Invalid",
            "last_name": "Email",
            "email": "not-an-email",
            "enrollment_number": "STU999",
            "major": "CS"
        })
        assert res.status_code == 422
        print("  ✓ Invalid email rejected with 422 Unprocessable Entity")

        # Invalid GPA > 4.0
        res = await client.post("/api/students", json={
            "first_name": "Invalid",
            "last_name": "GPA",
            "email": "gpa@test.com",
            "enrollment_number": "STU998",
            "major": "CS",
            "gpa": 5.0
        })
        assert res.status_code == 422
        print("  ✓ Invalid GPA (>4.0) rejected with 422 Unprocessable Entity")

    print("\n==================================================")
    print("ALL TESTS PASSED SUCCESSFULLY! 🚀")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
