from datetime import date

from app.modules.attendance.schemas import AttendanceSessionCreate
from app.modules.attendance.service import AttendanceService
from app.modules.students.schemas import GuardianCreate, StudentCreate
from app.modules.students.service import StudentService
from tests.unit.test_timetable_service import seed


def test_attendance_api_marks_records(client, db_session):
    _, version, _, _, slot = seed(db_session)
    student = StudentService(db_session, "college-a").create_student(
        StudentCreate(
            admission_number="ADM-API-1",
            first_name="Sara",
            last_name="Ahmed",
            date_of_birth=date(2014, 2, 1),
            gender="female",
            address="Main campus road",
            program="Middle Science",
            current_class="Class 6",
            current_section="A",
            academic_session="2026-2027",
            enrollment_date=date(2026, 4, 1),
            guardians=[
                GuardianCreate(
                    full_name="Parent Ahmed",
                    relationship="mother",
                    mobile="03111111111",
                    is_primary=True,
                )
            ],
        )
    )
    attendance = AttendanceService(db_session, "college-a").create_session(
        AttendanceSessionCreate(
            session_id=version.session_id,
            section_id=version.section_id,
            attendance_date=date(2026, 4, 6),
            teacher_id="t-1",
            teacher_name="Ada Teacher",
            time_slot_id=slot.id,
        )
    )
    response = client.post(
        f"/api/v1/attendance/sessions/{attendance.id}/records",
        json={"records": [{"student_id": student.id, "status": "present"}]},
        headers={"X-College-Id": "college-a"},
    )
    assert response.status_code == 200
    assert response.json()[0]["student_id"] == student.id
