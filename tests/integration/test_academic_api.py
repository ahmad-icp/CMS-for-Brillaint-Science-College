


def test_academic_configuration_flow_and_permissions(client):
    blocked = client.post("/api/v1/academic/institutions", json={"name":"Demo College","code":"DC"}, headers={"X-Role":"teacher"})
    assert blocked.status_code == 403
    institution = client.post("/api/v1/academic/institutions", json={"name":"Demo College","code":"DC"}, headers={"X-Role":"administrator"}).json()
    department = client.post("/api/v1/academic/departments", json={"institution_id": institution["id"], "name":"Science", "code":"SCI"}, headers={"X-Role":"administrator"}).json()
    session = client.post("/api/v1/academic/sessions", json={"name":"2026-2027", "start_date":"2026-04-01", "end_date":"2027-03-31"}, headers={"X-Role":"administrator"}).json()
    program = client.post("/api/v1/academic/programs", json={"department_id": department["id"], "name":"Science", "code":"SCI-P", "duration_years":3}, headers={"X-Role":"administrator"}).json()
    klass = client.post("/api/v1/academic/classes", json={"program_id": program["id"], "session_id": session["id"], "name":"Class 6"}, headers={"X-Role":"administrator"}).json()
    duplicate = client.post("/api/v1/academic/classes", json={"program_id": program["id"], "session_id": session["id"], "name":"class 6"}, headers={"X-Role":"administrator"})
    assert duplicate.status_code == 409
    section = client.post("/api/v1/academic/sections", json={"class_id": klass["id"], "name":"A", "capacity":40}, headers={"X-Role":"administrator"}).json()
    subject = client.post("/api/v1/academic/subjects", json={"department_id": department["id"], "code":"MATH", "name":"Mathematics", "weekly_periods":5}, headers={"X-Role":"administrator"}).json()
    assignment = client.post("/api/v1/academic/teacher-assignments", json={"teacher_id":"t-1", "teacher_name":"Ada Teacher", "section_id":section["id"], "subject_id":subject["id"], "weekly_periods":5}, headers={"X-Role":"administrator"})
    assert assignment.status_code == 201
    workload = client.get("/api/v1/academic/teacher-assignments/t-1/workload", headers={"X-Role":"teacher"})
    assert workload.status_code == 200
    assert workload.json()["assigned_periods"] == 5
